const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

let activeRefreshPromise: Promise<string | null> | null = null;

const getCache = new Map<string, { data: any; timestamp: number }>();
const activeGetRequests = new Map<string, Promise<any>>();
const CACHE_TTL_MS = 5000;

async function executeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Attach JWT Bearer token from localStorage if available
  try {
    const token = localStorage.getItem('office_leaks_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  } catch {
    // localStorage may be unavailable in some contexts
  }

  const config: RequestInit = {
    ...options,
    headers,
    credentials: 'include', // Automatically send cookies (like HttpOnly refresh_token)
  };

  let response = await fetch(url, config);

  // If 401 Unauthorized, intercept and try token refresh or fallback retry
  if (response.status === 401 && endpoint !== '/user/token/refresh/' && endpoint !== '/user/login/') {
    try {
      if (!activeRefreshPromise) {
        const hasAccessToken = localStorage.getItem('office_leaks_token');
        if (hasAccessToken) {
          // Attempt to refresh the access token and save the promise
          activeRefreshPromise = (async () => {
            try {
              const refreshResponse = await fetch(`${BASE_URL}/user/token/refresh/`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                credentials: 'include', // Ensure the browser sends HttpOnly cookies
              });

              if (refreshResponse.ok) {
                const refreshData = await refreshResponse.json();
                const newAccessToken = refreshData.access;
                if (newAccessToken) {
                  localStorage.setItem('office_leaks_token', newAccessToken);
                  return newAccessToken;
                }
              }
              // Both access and refresh tokens are expired
              localStorage.removeItem('office_leaks_token');
              localStorage.removeItem('office_leaks_user');
              window.dispatchEvent(new CustomEvent('auth-expired'));
              return null;
            } catch {
              return null;
            } finally {
              activeRefreshPromise = null;
            }
          })();
        } else {
          // No access token available, retry without Authorization header
          localStorage.removeItem('office_leaks_token');
        }
      }

      // Wait for the single active refresh promise to resolve
      const tokenToUse = activeRefreshPromise ? await activeRefreshPromise : null;

      if (tokenToUse) {
        headers['Authorization'] = `Bearer ${tokenToUse}`;
        response = await fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });
      } else {
        delete headers['Authorization'];
        response = await fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });
      }
    } catch {
      // Fallback: retry without Authorization header if refreshing crashes
      delete headers['Authorization'];
      response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      });
    }
  }

  if (!response.ok) {
    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }
    throw new ApiError(
      `API request failed with status ${response.status}`,
      response.status,
      errorData
    );
  }

  if (response.status === 24 || response.status === 204) {
    return {} as T;
  }

  return response.json();
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const method = options.method || 'GET';

  if (method !== 'GET') {
    getCache.clear();
    return executeRequest<T>(endpoint, options);
  }

  // Generate cache key based on endpoint and options
  const cacheKey = `${endpoint}:${JSON.stringify(options.headers || {})}`;

  // Check valid cache
  const cached = getCache.get(cacheKey);
  if (cached && (Date.now() - cached.timestamp < CACHE_TTL_MS)) {
    return cached.data;
  }

  // Check active concurrent request
  if (activeGetRequests.has(cacheKey)) {
    return activeGetRequests.get(cacheKey)!;
  }

  const promise = (async () => {
    try {
      return await executeRequest<T>(endpoint, options);
    } finally {
      activeGetRequests.delete(cacheKey);
    }
  })();

  activeGetRequests.set(cacheKey, promise);

  try {
    const result = await promise;
    getCache.set(cacheKey, { data: result, timestamp: Date.now() });
    return result;
  } catch (error) {
    throw error;
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'DELETE',
      body: body ? JSON.stringify(body) : undefined,
    }),
};
