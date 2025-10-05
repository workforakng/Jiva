from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging
from firebase_admin import auth

from app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get Firestore service
async def get_firestore_service():
    return FirestoreService()

# Dependency to get current user from token
async def get_current_user_from_token(token_data: dict = Depends(lambda: None)):
    """Get current user from decoded token"""
    # This will be injected by the main app's dependency
    return token_data

@router.get("/")
async def get_health_records(
    user_id: Optional[str] = Query(None, description="User ID to filter records"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    page: int = Query(1, ge=1, description="Page number"),
    record_type: Optional[str] = Query(None, description="Filter by record type"),
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get health records for the authenticated user"""
    try:
        # Use current user's ID if not provided
        target_user_id = user_id or current_user.get('uid')
        
        if not target_user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Ensure user can only access their own records
        if target_user_id != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Build filters
        filters = [('user_id', '==', target_user_id)]
        if record_type:
            filters.append(('type', '==', record_type))
        
        # Get records from Firestore
        records = await firestore_service.query_documents(
            collection='health_records',
            filters=filters,
            order_by='date',
            limit=limit
        )
        
        # Calculate pagination
        total_records = len(records)  # This is simplified; in production, you'd get total count separately
        
        return {
            "success": True,
            "data": {
                "records": records,
                "total": total_records,
                "page": page,
                "limit": limit,
                "has_more": total_records == limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch health records")

@router.get("/{record_id}")
async def get_health_record(
    record_id: str,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get a specific health record by ID"""
    try:
        # Get the record
        record = await firestore_service.get_health_record(record_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Health record not found")
        
        # Ensure user can only access their own records
        if record.get('user_id') != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "data": record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch health record")

@router.post("/")
async def create_health_record(
    record_data: dict,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Create a new health record"""
    try:
        # Ensure the record belongs to the current user
        record_data['user_id'] = current_user.get('uid')
        
        # Validate required fields
        required_fields = ['date', 'type', 'facility', 'biomarkers']
        for field in required_fields:
            if field not in record_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create the record
        record_id = await firestore_service.create_health_record(record_data)
        
        # Get the created record
        created_record = await firestore_service.get_health_record(record_id)
        
        return {
            "success": True,
            "message": "Health record created successfully",
            "data": created_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating health record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create health record")

@router.put("/{record_id}")
async def update_health_record(
    record_id: str,
    update_data: dict,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update a health record"""
    try:
        # Get the existing record
        existing_record = await firestore_service.get_health_record(record_id)
        
        if not existing_record:
            raise HTTPException(status_code=404, detail="Health record not found")
        
        # Ensure user can only update their own records
        if existing_record.get('user_id') != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove fields that shouldn't be updated
        update_data.pop('id', None)
        update_data.pop('user_id', None)
        update_data.pop('created_at', None)
        
        # Update the record
        await firestore_service.update_health_record(record_id, update_data)
        
        # Get the updated record
        updated_record = await firestore_service.get_health_record(record_id)
        
        return {
            "success": True,
            "message": "Health record updated successfully",
            "data": updated_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating health record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update health record")

@router.delete("/{record_id}")
async def delete_health_record(
    record_id: str,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Delete a health record (soft delete)"""
    try:
        # Get the existing record
        existing_record = await firestore_service.get_health_record(record_id)
        
        if not existing_record:
            raise HTTPException(status_code=404, detail="Health record not found")
        
        # Ensure user can only delete their own records
        if existing_record.get('user_id') != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Soft delete the record
        await firestore_service.delete_health_record(record_id)
        
        return {
            "success": True,
            "message": "Health record deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting health record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete health record")

@router.get("/stats/summary")
async def get_health_stats(
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get health statistics summary for the user"""
    try:
        user_id = current_user.get('uid')
        
        # Get all user's health records
        records = await firestore_service.get_user_health_records(user_id, limit=1000)
        
        # Calculate statistics
        total_records = len(records)
        
        # Count by type
        type_counts = {}
        normal_count = 0
        recent_record = None
        
        for record in records:
            # Count by type
            record_type = record.get('type', 'Unknown')
            type_counts[record_type] = type_counts.get(record_type, 0) + 1
            
            # Count normal results
            biomarkers = record.get('biomarkers', {})
            if all(b.get('status') == 'normal' for b in biomarkers.values()):
                normal_count += 1
            
            # Get most recent record
            if not recent_record or record.get('date', '') > recent_record.get('date', ''):
                recent_record = record
        
        return {
            "success": True,
            "data": {
                "total_records": total_records,
                "normal_results": normal_count,
                "type_distribution": type_counts,
                "recent_record_date": recent_record.get('date') if recent_record else None,
                "recent_record_type": recent_record.get('type') if recent_record else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting health stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health statistics")
