// Health Record Types
export interface Biomarker {
  value: number | string;
  unit: string;
  range: string;
  status: 'normal' | 'borderline' | 'abnormal';
  name?: string;
}

export interface HealthRecord {
  id: string;
  userId: string;
  date: string;
  type: string;
  facility: string;
  biomarkers: Record<string, Biomarker>;
  originalDocument: string;
  documentUrl?: string;
  createdAt: string;
  updatedAt: string;
}

// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  phone: string;
  dateOfBirth: string;
  bloodGroup?: string;
  allergies?: string[];
  chronicConditions?: string[];
  emergencyContact?: {
    name: string;
    phone: string;
    relationship: string;
  };
  createdAt: string;
}

// Upload Types
export interface UploadProgress {
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
}

export interface DocumentUpload {
  uri: string;
  name: string;
  type: string;
  size: number;
}
