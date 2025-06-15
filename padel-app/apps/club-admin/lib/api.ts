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
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return `${baseUrl}/api/v1`;
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

  post: async <T>(path: string, body: any, options?: { headers?: Record<string, string> }): Promise<T> => {
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

export const fetchBookings = async (startDate: Date, endDate: Date): Promise<Booking[]> => {
  const formattedStartDate = format(startDate, 'yyyy-MM-dd');
  const formattedEndDate = format(endDate, 'yyyy-MM-dd');
  
  const response = await apiClient.get<{ courts: Court[], bookings: Booking[] }>(
    `/admin/my-club/schedule`, { start_date: formattedStartDate, end_date: formattedEndDate }
  );
  
  return response.bookings || [];
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

export const updateClub = async (clubId: number, data: Partial<Club>): Promise<Club> => {
  if (!clubId) {
    throw new Error("Club ID is required to update club details.");
  }
  return apiClient.put(`/admin/club/${clubId}`, data);
};

export const registerAdmin = async (data: AdminRegistrationData): Promise<AuthResponse> => {
  return apiClient.post('/auth/register-admin', data);
};

export const createClub = async (data: ClubData, token?: string): Promise<Club> => {
  const headers = new Headers(getAuthHeaders());
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return apiClient.post<Club>('/clubs', data, { headers: headers as any });
};

export const createCourt = async (data: CourtData, token?: string): Promise<Court> => {
  const headers = new Headers(getAuthHeaders());
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return apiClient.post<Court>('/courts', data, { headers: headers as any });
};

export const getMe = async (): Promise<User> => {
  return apiClient.get<User>('/auth/users/me');
}; 