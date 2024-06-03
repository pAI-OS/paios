import { DataProvider } from 'react-admin';
//import jsonServerProvider from 'ra-data-json-server';
import simpleRestProvider from 'ra-data-simple-rest';
import { httpClient, apiBase } from './apiBackend';

export const dataProvider: DataProvider = simpleRestProvider(apiBase, httpClient);

export default dataProvider;
