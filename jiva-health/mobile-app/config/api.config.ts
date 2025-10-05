import Constants from 'expo-constants';

export const API_CONFIG = {
  baseURL: Constants.expoConfig?.extra?.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: parseInt(Constants.expoConfig?.extra?.EXPO_PUBLIC_API_TIMEOUT || '30000'),
  headers: {
    'Content-Type': 'application/json',
  },
};

export const ENDPOINTS = {
  // Auth
  login: '/auth/login',
  register: '/auth/register',
  logout: '/auth/logout',
  
  // Health Records
  healthRecords: '/api/health-records',
  healthRecordById: (id: string) => `/api/health-records/${id}`,
  
  // Upload
  uploadDocument: '/api/upload/document',
  processDocument: '/api/upload/process',
  
  // User
  userProfile: '/api/user/profile',
  updateProfile: '/api/user/profile/update',
};
