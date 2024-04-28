import { DataProvider } from 'react-admin';
import jsonServerProvider from 'ra-data-json-server';
import { httpClient, apiBase } from './apiBackend';

export const dataProvider: DataProvider = jsonServerProvider(apiBase, httpClient);
