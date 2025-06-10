import { getCookie } from 'cookies-next';
import { formatErrorMessage } from './errorHandler';
import { showErrorToast } from './notifications';
import {
  DashboardSummary,
  Booking,
  BookingDetails,
  Game,
  Court,
  Club,
} from './types';

const getApiUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || '/api/v1';
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
        throw await response.json();
      }
      return response.json() as Promise<T>;
    } catch (error) {
      const formattedError = formatErrorMessage(error);
      showErrorToast(formattedError);
      throw formattedError;
    }
  },

  post: async <T>(path: string, body: any, options?: { headers?: Record<string, string> }): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'POST',
        headers: options?.headers || getAuthHeaders(),
        body: options?.headers ? body : JSON.stringify(body),
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

  put: async <T>(path: string, body: any): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
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

  delete: async <T>(path: string): Promise<T> => {
    try {
      const response = await fetch(`${getApiUrl()}${path}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
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