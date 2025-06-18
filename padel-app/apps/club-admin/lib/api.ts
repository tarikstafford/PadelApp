import { getCookie } from 'cookies-next';
import { formatErrorMessage } from './errorHandler';
import { showErrorToast } from './notifications';
import {
  DashboardSummary,
  Booking,
  Game,
  Court,
  Club,
  AdminRegistrationData,
  AuthResponse,
  ClubData,
  User,
  CourtData
} from './types';
import { format } from 'date-fns';

const getApiUrl = () => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  return baseUrl;
};

const getAuthHeaders = (): HeadersInit => {
  const headers = new Headers();
  headers.append('Content-Type', 'application/json');

  const token = getCookie('token');
  if (token) {
    headers.append('Authorization', `Bearer ${token}`);
  }
  return headers;
};

export const apiClient = {
  get: async <T>(path: string, params?: Record<string, any>): Promise<T> => {
    try {
      const url = new URL(`${getApiUrl()}${path}`);
      if (params) {
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
      }
      const response = await fetch(url.toString(), {
        headers: getAuthHeaders(),
      });
      if (!response.ok) {
        let errorBody;
        try {
          errorBody = await response.json();
        } catch (e) {
          errorBody = { detail: `Request failed with status ${response.status}` };
        }
        throw errorBody;
      }
      return response.json() as Promise<T>;
    } catch (error: any) {
      if (typeof error === 'object' && error !== null && !error.detail && !error.message) {
        error.detail = 'An unexpected error occurred. The server returned an empty error response.';
      }
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },

  post: async <T>(path: string, body: any, options?: { headers?: Record<string, string>; silenceError?: boolean }): Promise<T> => {
    try {
      const isFormData = body instanceof FormData;
      const headers = options?.headers || getAuthHeaders();
      
      if (isFormData && headers instanceof Headers) {
        (headers as Headers).delete('Content-Type');
      }

      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'POST',
        headers: headers as HeadersInit,
        body: isFormData ? body : JSON.stringify(body),
      });

      if (!response.ok) {
        // Always try to parse the error body
        const errorBody = await response.json().catch(() => ({ 
          detail: `Request failed with status ${response.status} and no JSON error body.` 
        }));
        throw errorBody; // Throw the original error body from the API
      }
      return response.json() as Promise<T>;
    } catch (error: any) {
      // If we are explicitly silencing errors, just rethrow without logging/toasting
      if (options?.silenceError) {
        throw error;
      }
      
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      // Re-throw the original error so the calling function can inspect it
      throw error;
    }
  },

  put: async <T>(path: string, body: any): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        let errorBody;
        try {
          errorBody = await response.json();
        } catch (e) {
          errorBody = { detail: `Request failed with status ${response.status}` };
        }
        throw errorBody;
      }
      return response.json() as Promise<T>;
    } catch (error: any) {
      if (typeof error === 'object' && error !== null && !error.detail && !error.message) {
        error.detail = 'An unexpected error occurred. The server returned an empty error response.';
      }
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },

  delete: async <T>(path: string): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (!response.ok) {
        let errorBody;
        try {
          errorBody = await response.json();
        } catch (e) {
          errorBody = { detail: `Request failed with status ${response.status}` };
        }
        throw errorBody;
      }
      return response.json() as Promise<T>;
    } catch (error: any) {
      if (typeof error === 'object' && error !== null && !error.detail && !error.message) {
        error.detail = 'An unexpected error occurred. The server returned an empty error response.';
      }
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },
};

export const fetchDashboardSummary = async (clubId: number): Promise<DashboardSummary> => {
  if (!clubId) {
    throw new Error("Club ID is required to fetch dashboard summary.");
  }
  return apiClient.get(`/admin/club/${clubId}/dashboard-summary`);
};

export const fetchBookings = async (
  clubId: number,
  params: {
    start_date?: string;
    end_date?: string;
    court_id?: number;
    status?: string;
    search?: string;
    page?: number;
    pageSize?: number;
  }
): Promise<{ bookings: Booking[]; pageCount: number }> => {
  return apiClient.get(`/admin/club/${clubId}/bookings`, params);
};

export const fetchGameDetails = async (bookingId: number): Promise<Game> => {
  if (!bookingId) {
    throw new Error("Booking ID is required to fetch game details.");
  }
  return apiClient.get(`/admin/bookings/${bookingId}/game`);
};

export const fetchCourts = async (clubId: number): Promise<Court[]> => {
  if (!clubId) {
    throw new Error("Club ID is required to fetch courts.");
  }
  return apiClient.get(`/admin/club/${clubId}/courts`);
};

export const fetchCourtSchedule = async (clubId: number, date: string): Promise<{ courts: Court[]; bookings: Booking[] }> => {
  if (!clubId) {
    throw new Error("Club ID is required to fetch schedule.");
  }
  return apiClient.get(`/admin/club/${clubId}/schedule`, { date });
};

export const fetchClubDetails = async (clubId: number): Promise<Club> => {
  if (!clubId) {
    throw new Error("Club ID is required to fetch club details.");
  }
  return apiClient.get(`/admin/club/${clubId}`);
};

export const updateClub = async (clubId: number, data: Partial<Club> | FormData): Promise<Club> => {
  if (!clubId) {
    throw new Error("Club ID is required to update club details.");
  }
  return apiClient.put(`/admin/club/${clubId}`, data);
};

export const registerAdmin = async (data: AdminRegistrationData): Promise<AuthResponse> => {
  return apiClient.post('/auth/register-admin', data);
};

export const createClub = async (data: ClubData | FormData, token?: string): Promise<Club> => {
  const headers = getAuthHeaders();
  if (token && headers instanceof Headers) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return apiClient.post('/admin/my-club', data, { headers: headers as Record<string, string> });
};

export const createCourt = async (data: CourtData, token?: string): Promise<Court> => {
  const headers = getAuthHeaders();
  if (token && headers instanceof Headers) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return apiClient.post('/courts', data, { headers: headers as Record<string, string> });
};

export const getMe = async (): Promise<User> => {
  return apiClient.get('/auth/users/me');
}; 