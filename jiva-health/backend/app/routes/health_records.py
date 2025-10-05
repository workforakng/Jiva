from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Dependencies
async def get_firestore_service():
    return FirestoreService()

@router.post("/register")
async def register_user(
    user_data: Dict[str, Any] = Body(...),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Register a new user (this will be called after Firebase client-side registration)"""
    try:
        # Extract user information
        uid = user_data.get('uid')
        email = user_data.get('email')
        name = user_data.get('name', '')
        phone = user_data.get('phone', '')
        
        if not uid or not email:
            raise HTTPException(status_code=400, detail="UID and email are required")
        
        # Verify the user exists in Firebase Auth
        try:
            firebase_user = auth.get_user(uid)
        except auth.UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found in Firebase")
        
        # Check if user profile already exists
        existing_profile = await firestore_service.get_user_profile(uid)
        if existing_profile:
            raise HTTPException(status_code=400, detail="User profile already exists")
        
        # Create user profile in Firestore
        profile_data = {
            'id': uid,
            'email': email,
            'name': name,
            'phone': phone,
            'date_of_birth': user_data.get('date_of_birth'),
            'blood_group': user_data.get('blood_group'),
            'allergies': user_data.get('allergies', []),
            'chronic_conditions': user_data.get('chronic_conditions', []),
            'emergency_contact': user_data.get('emergency_contact'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'profile_completed': bool(name and phone),
            'last_login': datetime.utcnow().isoformat()
        }
        
        await firestore_service.create_user_profile(uid, profile_data)
        
        logger.info(f"User profile created for UID: {uid}")
        
        return {
            "success": True,
            "message": "User profile created successfully",
            "data": {
                "uid": uid,
                "email": email,
                "name": name,
                "profile_completed": profile_data['profile_completed']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user profile")

@router.post("/login")
async def login_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Login user (verify token and update last login)"""
    try:
        # Verify Firebase ID token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # Get user profile
        user_profile = await firestore_service.get_user_profile(uid)
        
        if not user_profile:
            # If profile doesn't exist, create a minimal one
            firebase_user = auth.get_user(uid)
            profile_data = {
                'id': uid,
                'email': firebase_user.email,
                'name': firebase_user.display_name or '',
                'phone': firebase_user.phone_number or '',
                'allergies': [],
                'chronic_conditions': [],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'profile_completed': False,
                'last_login': datetime.utcnow().isoformat()
            }
            await firestore_service.create_user_profile(uid, profile_data)
            user_profile = profile_data
        else:
            # Update last login
            await firestore_service.update_user_profile(uid, {
                'last_login': datetime.utcnow().isoformat()
            })
        
        logger.info(f"User logged in: {uid}")
        
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "user": user_profile,
                "token_valid": True,
                "expires_in": decoded_token.get('exp', 0) - int(datetime.utcnow().timestamp())
            }
        }
        
    except auth.InvalidIdTokenError:
        logger.warning("Invalid ID token provided")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except auth.ExpiredIdTokenError:
        logger.warning("Expired ID token provided")
        raise HTTPException(status_code=401, detail="Authentication token expired")
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Logout user (revoke token and update logout time)"""
    try:
        # Verify token first
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # Revoke refresh tokens for the user
        auth.revoke_refresh_tokens(uid)
        
        # Update user profile with logout time
        await firestore_service.update_user_profile(uid, {
            'last_logout': datetime.utcnow().isoformat()
        })
        
        logger.info(f"User logged out: {uid}")
        
        return {
            "success": True,
            "message": "Logout successful"
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/profile")
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Get current user profile"""
    try:
        # Verify token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # Get user profile
        user_profile = await firestore_service.get_user_profile(uid)
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "success": True,
            "data": user_profile
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.put("/profile")
async def update_user_profile(
    update_data: Dict[str, Any] = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Update user profile"""
    try:
        # Verify token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # Remove fields that shouldn't be updated
        protected_fields = ['id', 'email', 'uid', 'created_at']
        for field in protected_fields:
            update_data.pop(field, None)
        
        # Add updated timestamp
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Check if profile is now complete
        required_fields = ['name', 'phone']
        current_profile = await firestore_service.get_user_profile(uid)
        if current_profile:
            profile_completed = all(
                update_data.get(field) or current_profile.get(field) 
                for field in required_fields
            )
            update_data['profile_completed'] = profile_completed
        
        # Update user profile
        await firestore_service.update_user_profile(uid, update_data)
        
        # Get updated profile
        updated_profile = await firestore_service.get_user_profile(uid)
        
        logger.info(f"User profile updated: {uid}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": updated_profile
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

@router.post("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify if the provided token is valid"""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        
        return {
            "success": True,
            "message": "Token is valid",
            "data": {
                "uid": decoded_token['uid'],
                "email": decoded_token.get('email'),
                "email_verified": decoded_token.get('email_verified', False),
                "expires_at": decoded_token.get('exp', 0),
                "issued_at": decoded_token.get('iat', 0)
            }
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Authentication token expired")
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail="Token verification failed")

@router.post("/refresh-token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Refresh user token (this is typically handled client-side by Firebase SDK)"""
    try:
        # Verify current token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # In Firebase, token refresh is handled client-side
        # This endpoint can be used to verify the refreshed token
        return {
            "success": True,
            "message": "Token verified. Use Firebase SDK client-side to refresh tokens.",
            "data": {
                "uid": uid,
                "should_refresh_client_side": True
            }
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        logger.error(f"Error in refresh token endpoint: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.delete("/account")
async def delete_user_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    firestore_service: FirestoreService = Depends(get_firestore_service),
    confirmation: Dict[str, str] = Body(...)
):
    """Delete user account (soft delete - mark as deleted)"""
    try:
        # Verify token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # Check confirmation
        if confirmation.get('confirm_delete') != 'DELETE_MY_ACCOUNT':
            raise HTTPException(
                status_code=400, 
                detail="Please provide confirmation with 'confirm_delete': 'DELETE_MY_ACCOUNT'"
            )
        
        # Soft delete user profile
        await firestore_service.update_user_profile(uid, {
            'deleted': True,
            'deleted_at': datetime.utcnow().isoformat(),
            'account_status': 'deleted'
        })
        
        # Soft delete all user's health records
        user_records = await firestore_service.get_user_health_records(uid, limit=1000)
        for record in user_records:
            await firestore_service.delete_health_record(record['id'])
        
        logger.info(f"User account soft deleted: {uid}")
        
        return {
            "success": True,
            "message": "Account deleted successfully. Your data has been marked for deletion."
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")

@router.get("/user-stats")
async def get_user_statistics(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Get user account statistics"""
    try:
        # Verify token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        # Get user profile
        user_profile = await firestore_service.get_user_profile(uid)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get health records count
        health_records = await firestore_service.get_user_health_records(uid, limit=1000)
        
        # Calculate statistics
        account_age_days = 0
        if user_profile.get('created_at'):
            created_date = datetime.fromisoformat(user_profile['created_at'].replace('Z', '+00:00'))
            account_age_days = (datetime.utcnow() - created_date.replace(tzinfo=None)).days
        
        return {
            "success": True,
            "data": {
                "account_created": user_profile.get('created_at'),
                "account_age_days": account_age_days,
                "profile_completed": user_profile.get('profile_completed', False),
                "total_health_records": len(health_records),
                "last_login": user_profile.get('last_login'),
                "last_activity": user_profile.get('updated_at')
            }
        }
        
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user statistics")
