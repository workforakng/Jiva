from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self):
        self.db = firestore.Client(project=settings.firebase_project_id)
    
    async def test_connection(self) -> bool:
        """Test Firestore connection"""
        try:
            # Try to read from a test collection
            self.db.collection('test').limit(1).get()
            return True
        except Exception as e:
            logger.error(f"Firestore connection test failed: {str(e)}")
            raise e
    
    # User Profile operations
    async def create_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        try:
            user_dict = dict(user_data)
            user_dict['id'] = user_id
            user_dict['created_at'] = datetime.utcnow().isoformat()
            user_dict['updated_at'] = datetime.utcnow().isoformat()
            
            self.db.collection('users').document(user_id).set(user_dict)
            logger.info(f"User profile created: {user_id}")
            return user_dict
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            raise e
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise e
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            update_dict = dict(update_data)
            update_dict['updated_at'] = datetime.utcnow().isoformat()
            
            self.db.collection('users').document(user_id).update(update_dict)
            logger.info(f"User profile updated: {user_id}")
            
            # Return updated profile
            return await self.get_user_profile(user_id)
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise e
    
    # Health record operations
    async def create_health_record(self, record_data: Dict[str, Any]) -> str:
        """Create a new health record and return the record ID"""
        try:
            record_dict = dict(record_data)
            record_dict['created_at'] = datetime.utcnow().isoformat()
            record_dict['updated_at'] = datetime.utcnow().isoformat()
            
            # Add document to collection and get the reference
            _, doc_ref = self.db.collection('health_records').add(record_dict)
            logger.info(f"Health record created: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating health record: {str(e)}")
            raise e
    
    async def get_user_health_records(
        self, 
        user_id: str, 
        limit: Optional[int] = None,
        cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get health records for a user with optional pagination"""
        try:
            query = self.db.collection('health_records').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).order_by('created_at', direction=firestore.Query.DESCENDING)
            
            if limit:
                query = query.limit(limit)
            
            if cursor:
                # Get the cursor document for pagination
                cursor_doc = self.db.collection('health_records').document(cursor).get()
                if cursor_doc.exists:
                    query = query.start_after(cursor_doc)
            
            docs = query.stream()
            records = []
            
            for doc in docs:
                record_dict = doc.to_dict()
                record_dict['id'] = doc.id
                records.append(record_dict)
            
            logger.info(f"Retrieved {len(records)} health records for user {user_id}")
            return records
        except Exception as e:
            logger.error(f"Error getting health records: {str(e)}")
            raise e
    
    async def get_health_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific health record"""
        try:
            doc = self.db.collection('health_records').document(record_id).get()
            if doc.exists:
                record_dict = doc.to_dict()
                record_dict['id'] = doc.id
                return record_dict
            return None
        except Exception as e:
            logger.error(f"Error getting health record: {str(e)}")
            raise e
    
    async def update_health_record(self, record_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a health record"""
        try:
            update_dict = dict(update_data)
            update_dict['updated_at'] = datetime.utcnow().isoformat()
            
            self.db.collection('health_records').document(record_id).update(update_dict)
            logger.info(f"Health record updated: {record_id}")
            
            # Return updated record
            return await self.get_health_record(record_id)
        except Exception as e:
            logger.error(f"Error updating health record: {str(e)}")
            raise e
    
    async def delete_health_record(self, record_id: str) -> bool:
        """Delete a health record (soft delete by default)"""
        try:
            # Soft delete - mark as deleted
            self.db.collection('health_records').document(record_id).update({
                'deleted': True,
                'deleted_at': datetime.utcnow().isoformat()
            })
            logger.info(f"Health record soft deleted: {record_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting health record: {str(e)}")
            raise e
    
    async def hard_delete_health_record(self, record_id: str) -> bool:
        """Permanently delete a health record"""
        try:
            self.db.collection('health_records').document(record_id).delete()
            logger.info(f"Health record hard deleted: {record_id}")
            return True
        except Exception as e:
            logger.error(f"Error hard deleting health record: {str(e)}")
            raise e
