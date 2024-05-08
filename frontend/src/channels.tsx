import React from 'react';
import { List, Datagrid, TextField, UrlField, Show, SimpleShowLayout } from 'react-admin';
import SyncAltIcon from '@mui/icons-material/SyncAlt';

export const ChannelList = () => (
  <List>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="name" />
      <UrlField source="uri" />
    </Datagrid>
  </List>
);

export const ChannelShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="name" />
      <UrlField source="uri" />
    </SimpleShowLayout>
  </Show>
);
