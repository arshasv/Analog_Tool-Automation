import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export interface IntrospectResponse {
  parameters: Array<{
    name: string;
    default: any;
    description: string;
    type: string;
  }>;
}

export interface RunResponse {
  process_id: string;
  message: string;
}

export interface StatusResponse {
  process_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'success' | 'SUCCESS';
  filename?: string;
  progress?: number;
  parameters?: Record<string, any>;
  mode?: 'simulate' | 'optimize' | string;
  metrics?: Record<string, any>;
  plots?: string[];
  results?: any;
  error?: string | null;
  created_at?: string;
  updated_at: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });

    this.client.interceptors.response.use(
      (response: any) => response,
      (error: AxiosError) => {
        console.error('API Error:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
        });
        return Promise.reject(error);
      }
    );
  }

  private handleError(error: any): ApiResponse<any> {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        return {
          success: false,
          error: (error.response.data as any)?.detail || `Server error: ${error.response.status}`,
          status: error.response.status,
        };
      } else if (error.request) {
        return {
          success: false,
          error: 'No response from backend. Is it running?',
        };
      }
    }
    return {
      success: false,
      error: error instanceof Error ? error.message : 'An unknown error occurred',
    };
  }

  async getHealth(): Promise<ApiResponse<{ status: string }>> {
    try {
      const response = await this.client.get('/health');
      return { success: true, data: response.data };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async introspect(file: File): Promise<ApiResponse<IntrospectResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await this.client.post('/api/v1/introspect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return { success: true, data: response.data };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async run(file: File, mode: 'simulate' | 'optimize', parameters?: Record<string, any>): Promise<ApiResponse<RunResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', mode);
      if (parameters) {
        formData.append('parameters', JSON.stringify(parameters));
      }
      const response = await this.client.post('/api/v1/run', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return { success: true, data: response.data };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getStatus(processId: string): Promise<ApiResponse<StatusResponse>> {
    try {
      const response = await this.client.get(`/api/v1/status/${processId}`);
      return { success: true, data: response.data };
    } catch (error) {
      return this.handleError(error);
    }
  }

  getDownloadUrl(processId: string): string {
    return `${API_BASE_URL}/api/v1/download/${processId}`;
  }
}

const apiClient = new ApiClient();
export default apiClient;
