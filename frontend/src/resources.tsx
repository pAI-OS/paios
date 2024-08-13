import { List, Datagrid, TextField, UrlField, Show, SimpleShowLayout } from 'react-admin';

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
