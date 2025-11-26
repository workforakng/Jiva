// Type definitions for Jiva Health Application

export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  dateOfBirth?: string;
  bloodGroup?: string;
  allergies?: string[];
  chronicConditions?: string[];
  emergencyContact?: EmergencyContact;
  createdAt: string;
  updatedAt?: string;
  profileCompleted?: boolean;
  lastLogin?: string;
}

export interface EmergencyContact {
  name: string;
  phone: string;
  relationship: string;
}

export interface Biomarker {
  value?: number;
  systolic?: number;  // For blood pressure
  diastolic?: number; // For blood pressure
  unit: string;
  range: string;
  status: 'normal' | 'borderline' | 'abnormal';
}

export interface ProcessingMetadata {
  ocr_pages?: number;
  ocr_blocks?: number;
  nlp_entities_found?: number;
  processed_at?: string;
}

export interface HealthRecord {
  id: string;
  userId: string;
  date: string;
  type: string;
  facility?: string;
  biomarkers?: Record<string, Biomarker>;
  originalDocument?: string;
  documentUrl?: string;
  ocrConfidence?: number;
  processingMetadata?: ProcessingMetadata;
  createdAt: string;
  updatedAt?: string;
  deleted?: boolean;
  deletedAt?: string;
}

export interface HealthRecordCreate {
  date: string;
  type: string;
  facility?: string;
  biomarkers?: Record<string, Biomarker>;
  originalDocument?: string;
  documentUrl?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface UploadResponse {
  record_id: string;
  record: HealthRecord;
  processing_summary: {
    ocr_confidence: number;
    biomarkers_extracted: number;
    text_length: number;
    processing_time: string;
  };
}

export interface UserStats {
  account_created: string;
  account_age_days: number;
  profile_completed: boolean;
  total_health_records: number;
  last_login?: string;
  last_activity?: string;
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface HealthRecordFilters {
  type?: string;
  dateFrom?: string;
  dateTo?: string;
  facility?: string;
}
