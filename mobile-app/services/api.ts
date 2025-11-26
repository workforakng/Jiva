import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG, ENDPOINTS } from '../config/api.config';
import { auth } from '../config/firebase.config';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      headers: API_CONFIG.headers,
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const currentUser = auth.currentUser;
        if (currentUser) {
          const token = await currentUser.getIdToken();
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          console.log('Unauthorized access - redirecting to login');
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic GET request
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  // Generic POST request
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  // Generic PUT request
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  // Generic DELETE request
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // Upload document with OCR processing
  async uploadAndProcessDocument(file: File | Blob, userId: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('userId', userId);

    return this.post(ENDPOINTS.uploadDocument, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // Get health records
  async getHealthRecords(userId: string) {
    return this.get(`${ENDPOINTS.healthRecords}?userId=${userId}`);
  }

  // Get single health record
  async getHealthRecord(recordId: string) {
    return this.get(ENDPOINTS.healthRecordById(recordId));
  }
}

export default new ApiService();
