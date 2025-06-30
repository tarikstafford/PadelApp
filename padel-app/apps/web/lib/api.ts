import { getCookie } from 'cookies-next';
import { formatErrorMessage } from './errorHandler';
import { showErrorToast } from './notifications';
import {
  DashboardSummary,
  Booking,
  // BookingDetails,
  Game,
  Court,
  Club,
  AdminRegistrationData,
  AuthResponse,
  ClubData,
  User,
  CourtData
} from './types';

const getApiUrl = () => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return `${baseUrl}/api/v1`;
};

const getAuthHeaders = (token?: string | null, authenticated = true): Headers => {
  const headers = new Headers();
  headers.append('Content-Type', 'application/json');

  if (authenticated) {
    const authToken = token || getCookie('token');
    if (authToken) {
      headers.append('Authorization', `Bearer ${authToken}`);
    }
  }
  return headers;
};

export const apiClient = {
  get: async <T>(path: string, params?: Record<string, any>, token?: string | null, authenticated = true): Promise<T> => {
    try {
      const url = new URL(`${getApiUrl()}${path}`);
      if (params) {
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
      }
      const requestHeaders = getAuthHeaders(token, authenticated);
      console.log(`[API CLIENT] GET ${url.toString()}`, { Authorization: requestHeaders.get('Authorization') });
      const response = await fetch(url.toString(), {
        headers: requestHeaders,
      });
      if (!response.ok) {
        throw await response.json();
      }
      return response.json() as Promise<T>;
    } catch (error) {
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },

  post: async <T>(path: string, body: any, options?: { headers?: Record<string, string>, token?: string | null }): Promise<T> => {
    try {
      const isFormData = body instanceof FormData;
      const headers = options?.headers || getAuthHeaders(options?.token);
      
      // Do not set Content-Type for FormData, browser does it with boundary
      if (isFormData && headers instanceof Headers) {
        (headers as Headers).delete('Content-Type');
      }

      console.log('API Client POST Request:', { path, body: isFormData ? 'FormData' : body });
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'POST',
        headers: headers,
        body: isFormData ? body : JSON.stringify(body),
      });
      if (!response.ok) {
        throw await response.json();
      }
      return response.json() as Promise<T>;
    } catch (error) {
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },

  put: async <T>(path: string, body: any, token?: string | null): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'PUT',
        headers: getAuthHeaders(token),
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        throw await response.json();
      }
      return response.json() as Promise<T>;
    } catch (error) {
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },

  delete: async <T>(path: string, token?: string | null): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'DELETE',
        headers: getAuthHeaders(token),
      });
      if (!response.ok) {
        throw await response.json();
      }
      return response.json() as Promise<T>;
    } catch (error) {
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
  if (!clubId) {
    throw new Error("Club ID is required to fetch bookings.");
  }
  return apiClient.get(`/admin/club/${clubId}/bookings`, params);
};

export const fetchGameDetails = async (bookingId: number): Promise<Game> => {
  if (!bookingId) {
    throw new Error("Booking ID is required to fetch game details.");
  }
  return apiClient.get<Game>(`/admin/bookings/${bookingId}/game`);
};

export const fetchCourts = async (clubId: number): Promise<Court[]> => {
  if (!clubId) {
    throw new Error("Club ID is required to fetch courts.");
  }
  return apiClient.get<Court[]>(`/admin/club/${clubId}/courts`);
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
  return apiClient.get<Club>(`/admin/club/${clubId}`);
};

export const updateClub = async (clubId: number, data: Partial<Club>): Promise<Club> => {
  if (!clubId) {
    throw new Error("Club ID is required to update club details.");
  }
  return apiClient.put<Club>(`/admin/club/${clubId}`, data);
};

export const registerAdmin = async (data: AdminRegistrationData): Promise<AuthResponse> => {
  return apiClient.post<AuthResponse>('/auth/register-admin', data);
};

export const createClub = async (data: ClubData, token?: string): Promise<Club> => {
  const headers = new Headers(getAuthHeaders(token));
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return apiClient.post<Club>('/clubs', data, { headers: headers as any });
};

export const createCourt = async (data: CourtData, token?: string): Promise<Court> => {
  const headers = new Headers(getAuthHeaders(token));
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return apiClient.post<Court>('/courts', data, { headers: headers as any });
};

export const getMe = async (): Promise<User> => {
  return apiClient.get<User>('/auth/users/me');
}; 