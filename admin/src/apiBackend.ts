import { fetchUtils } from 'react-admin';

export const apiBase = import.meta.env.VITE_JSON_SERVER_URL || 'http://localhost:3000';

export const httpClient = (url: string, options: any = {}) => {
    if (!options.headers) {
      options.headers = new Headers({ Accept: 'application/json' });
    }
    
    const token = import.meta.env.VITE_PAIOS_BEARER_TOKEN;
    options.headers.set('Authorization', `Bearer ${token}`);
    return fetchUtils.fetchJson(url, options);
  }
