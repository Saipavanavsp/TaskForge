let accessToken: string | null = null;

if (typeof window !== 'undefined') {
  accessToken = localStorage.getItem('taskforge_token');
}

export const setAuthToken = (token: string | null) => {
  accessToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('taskforge_token', token);
    } else {
      localStorage.removeItem('taskforge_token');
    }
  }
};

export const getAuthToken = () => accessToken;

export async function apiFetch<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  let res = await fetch(endpoint, {
    ...options,
    headers,
    credentials: 'include', // send httpOnly refresh cookies
  });

  // Attempt automatic refresh if 401
  if (res.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/refresh')) {
    try {
      const refreshRes = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        setAuthToken(data.access_token);
        headers.set('Authorization', `Bearer ${data.access_token}`);
        res = await fetch(endpoint, { ...options, headers, credentials: 'include' });
      } else {
        setAuthToken(null);
      }
    } catch {
      setAuthToken(null);
    }
  }

  if (!res.ok) {
    let errMessage = 'An error occurred';
    try {
      const errData = await res.json();
      errMessage = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errMessage = await res.text();
    }
    throw new Error(errMessage || `HTTP Error ${res.status}`);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}
