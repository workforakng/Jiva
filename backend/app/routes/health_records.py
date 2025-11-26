# backend/app/routes/health_records.py
from fastapi import APIRouter, HTTPException, Depends, Body, Query, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health Records"])
security = HTTPBearer()


# -------- Dependency: Firestore service factory --------
async def get_firestore_service() -> FirestoreService:
    """Return a FirestoreService instance"""
    return FirestoreService()


# -------- Dependency: Current user (verify Firebase token) --------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Verify Firebase ID token and return decoded token"""
    token = credentials.credentials
    try:
        decoded = firebase_auth.verify_id_token(token)
        return {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "email_verified": decoded.get("email_verified", False),
            "token_data": decoded,
        }
    except firebase_auth.ExpiredIdTokenError:
        logger.info("Expired Firebase token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token expired")
    except firebase_auth.InvalidIdTokenError:
        logger.info("Invalid Firebase token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")


# -------- Helper: standardize timestamps --------
def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


# -------- Routes --------

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_health_record(
    record: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Create a health record for the authenticated user"""
    try:
        uid = current_user["uid"]
        if not uid:
            raise HTTPException(status_code=401, detail="User authentication required")

        # Normalize and protect fields
        record_payload = dict(record)
        record_payload["user_id"] = uid
        record_payload.setdefault("date", datetime.utcnow().strftime("%Y-%m-%d"))
        record_payload["created_at"] = now_iso()
        record_payload["updated_at"] = now_iso()

        # Persist to Firestore
        record_id = await firestore_service.create_health_record(record_payload)
        created = await firestore_service.get_health_record(record_id)

        return {
            "success": True,
            "message": "Health record created",
            "data": {
                "record_id": record_id,
                "record": created
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating health record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create health record")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_health_records(
    limit: int = Query(20, gt=0, le=100),
    cursor: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """List health records for the authenticated user"""
    try:
        uid = current_user["uid"]
        if not uid:
            raise HTTPException(status_code=401, detail="User authentication required")

        records = await firestore_service.get_user_health_records(uid, limit=limit, cursor=cursor)

        return {
            "success": True,
            "data": {
                "records": records,
                "count": len(records),
                "next_cursor": None  # Implement cursor logic for pagination
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing health records: {e}")
        raise HTTPException(status_code=500, detail="Failed to list health records")


@router.get("/{record_id}", status_code=status.HTTP_200_OK)
async def get_health_record(
    record_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Retrieve a single health record by ID"""
    try:
        uid = current_user["uid"]
        rec = await firestore_service.get_health_record(record_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Record not found")

        # Ownership check
        if rec.get("user_id") != uid:
            raise HTTPException(status_code=403, detail="Access denied")

        return {"success": True, "data": rec}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching health record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch health record")


@router.put("/{record_id}", status_code=status.HTTP_200_OK)
async def update_health_record(
    record_id: str,
    update_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Update allowed fields on a health record"""
    try:
        uid = current_user["uid"]
        record = await firestore_service.get_health_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        if record.get("user_id") != uid:
            raise HTTPException(status_code=403, detail="Access denied")

        # Remove protected fields
        for p in ("id", "user_id", "created_at"):
            update_data.pop(p, None)

        update_data["updated_at"] = now_iso()

        updated = await firestore_service.update_health_record(record_id, update_data)

        return {"success": True, "message": "Record updated", "data": updated}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating health record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update health record")


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
async def delete_health_record(
    record_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Delete a health record (soft delete by default)"""
    try:
        uid = current_user["uid"]
        record = await firestore_service.get_health_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        if record.get("user_id") != uid:
            raise HTTPException(status_code=403, detail="Access denied")

        deleted = await firestore_service.delete_health_record(record_id)

        return {"success": True, "message": "Record deleted", "data": {"deleted": deleted}}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting health record {record_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete health record")
