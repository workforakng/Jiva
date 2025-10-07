# backend/app/models/health_record.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class Biomarker(BaseModel):
    """Individual biomarker reading with its value, unit, normal range, and status."""
    name: str = Field(..., example="hemoglobin")
    value: Optional[float] = Field(None, example=13.5)
    unit: Optional[str] = Field(None, example="g/dL")
    range: Optional[str] = Field(None, example="12.0-16.0")
    status: Optional[str] = Field(None, example="normal")


class ProcessingMetadata(BaseModel):
    """Metadata about OCR/NLP or document processing pipeline."""
    ocr_pages: Optional[int] = Field(0, example=1)
    ocr_blocks: Optional[int] = Field(0, example=15)
    nlp_entities_found: Optional[int] = Field(0, example=5)
    processed_at: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )


class HealthRecordBase(BaseModel):
    """Common fields for health records."""
    date: str = Field(..., example="2025-10-08")
    type: str = Field(..., example="Lipid Panel")
    facility: Optional[str] = Field(None, example="Apollo Diagnostics")
    biomarkers: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        example={"cholesterol": {"value": 180, "unit": "mg/dL", "status": "normal"}},
    )
    original_document: Optional[str] = Field(None, example="lipid_report.pdf")
    document_url: Optional[str] = Field(None, example="gs://jiva-health/documents/uid/abc123.pdf")
    ocr_confidence: Optional[float] = Field(0.0, ge=0, le=1)
    processing_metadata: Optional[ProcessingMetadata] = Field(default_factory=ProcessingMetadata)


class HealthRecordCreate(HealthRecordBase):
    """Schema for creating a new health record."""
    user_id: Optional[str] = Field(None, example="firebase-uid-123")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class HealthRecord(HealthRecordBase):
    """Full health record stored in Firestore."""
    id: Optional[str] = Field(None, example="record123")
    user_id: str = Field(..., example="firebase-uid-123")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    deleted: Optional[bool] = Field(False)
    deleted_at: Optional[str] = None
    account_status: Optional[str] = Field(None, example="active")

    class Config:
        orm_mode = True


class HealthRecordListResponse(BaseModel):
    """Response schema for multiple health records."""
    records: List[HealthRecord]
    count: int
    next_cursor: Optional[str] = None


class HealthRecordResponse(BaseModel):
    """Response schema for a single health record."""
    success: bool = True
    data: HealthRecord


class HealthRecordCreateResponse(BaseModel):
    """Response schema for record creation."""
    success: bool = True
    message: str = "Health record created"
    data: Dict[str, Any]
