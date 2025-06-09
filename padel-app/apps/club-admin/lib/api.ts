import { getCookie } from 'cookies-next';
import { formatErrorMessage } from './errorHandler';
import { showErrorToast } from './notifications';

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