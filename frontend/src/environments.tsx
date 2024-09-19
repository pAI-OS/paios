import { List, Datagrid, TextField, Create, Edit, SimpleForm, TextInput, Show, SimpleShowLayout, ReferenceInput, ReferenceField } from 'react-admin';

export const EnvironmentList = () => (
  <List>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <ReferenceField source="owner_id" reference="users" link="show">
        <TextField source="name" />
      </ReferenceField>
    </Datagrid>
  </List>
);

export const EnvironmentCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" multiline />
      <ReferenceInput source="owner_id" reference="users" />
    </SimpleForm>
  </Create>
);

export const EnvironmentEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" multiline />
      <ReferenceInput source="owner_id" reference="users" />
    </SimpleForm>
  </Edit>
);

export const EnvironmentShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <ReferenceField source="owner_id" reference="users" link="show">
        <TextField source="name" />
      </ReferenceField>
    </SimpleShowLayout>
  </Show>
);
