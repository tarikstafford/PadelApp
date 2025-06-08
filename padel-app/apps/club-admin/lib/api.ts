import { getCookie } from 'cookies-next';

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
  get: async <T>(path: string): Promise<T> => {
    const response = await fetch(`${getApiUrl()}${path}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json() as Promise<T>;
  },

  post: async <T>(path: string, body: any, options?: { headers?: Record<string, string> }): Promise<T> => {
    const response = await fetch(`${getApiUrl()}${path}`, {
      method: 'POST',
      headers: options?.headers || getAuthHeaders(),
      body: options?.headers ? body : JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json() as Promise<T>;
  },

  put: async <T>(path: string, body: any): Promise<T> => {
    const response = await fetch(`${getApiUrl()}${path}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json() as Promise<T>;
  },

  delete: async <T>(path: string): Promise<T> => {
    const response = await fetch(`${getApiUrl()}${path}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    return response.json() as Promise<T>;
  },
}; 