from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.config import settings
from app.models.health_record import HealthRecord, HealthRecordCreate
from app.models.user import User, UserCreate, UserUpdate

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
    
    # User operations
    async def create_user(self, user_data: UserCreate, user_id: str) -> User:
        """Create a new user"""
        try:
            user_dict = user_data.model_dump()
            user_dict.update({
                'id': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            
            self.db.collection('users').document(user_id).set(user_dict)
            
            return User(**user_dict)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise e
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return User(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise e
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """Update user data"""
        try:
            update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}
            update_dict['updated_at'] = datetime.utcnow()
            
            self.db.collection('users').document(user_id).update(update_dict)
            
            # Return updated user
            return await self.get_user(user_id)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise e
    
    # Health record operations
    async def create_health_record(self, record_data: HealthRecordCreate) -> HealthRecord:
        """Create a new health record"""
        try:
            record_dict = record_data.model_dump()
            record_dict.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            
            # Add document to collection and get the ID
            doc_ref = self.db.collection('health_records').add(record_dict)[1]
            record_dict['id'] = doc_ref.id
            
            return HealthRecord(**record_dict)
        except Exception as e:
            logger.error(f"Error creating health record: {str(e)}")
            raise e
    
    async def get_health_records(self, user_id: str, limit: Optional[int] = None) -> List[HealthRecord]:
        """Get health records for a user"""
        try:
            query = self.db.collection('health_records').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).order_by('date', direction=firestore.Query.DESCENDING)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            records = []
            
            for doc in docs:
                record_dict = doc.to_dict()
                record_dict['id'] = doc.id
                records.append(HealthRecord(**record_dict))
            
            return records
        except Exception as e:
            logger.error(f"Error getting health records: {str(e)}")
            raise e
    
    async def get_health_record(self, record_id: str) -> Optional[HealthRecord]:
        """Get a specific health record"""
        try:
            doc = self.db.collection('health_records').document(record_id).get()
            if doc.exists:
                record_dict = doc.to_dict()
                record_dict['id'] = doc.id
                return HealthRecord(**record_dict)
            return None
        except Exception as e:
            logger.error(f"Error getting health record: {str(e)}")
            raise e
    
    async def delete_health_record(self, record_id: str) -> bool:
        """Delete a health record"""
        try:
            self.db.collection('health_records').document(record_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting health record: {str(e)}")
            raise e
