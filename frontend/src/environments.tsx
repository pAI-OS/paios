import React from 'react';
import { List, Datagrid, TextField, Create, Edit, SimpleForm, TextInput, Show, SimpleShowLayout, ReferenceInput, ReferenceField } from 'react-admin';
import { useEnvironment } from './EnvironmentContext';
import { Select, MenuItem } from '@mui/material';

// New component
export const EnvironmentSelector = () => {
  const { currentEnvironment, setCurrentEnvironment, environments } = useEnvironment();

  return (
    <Select
      value={currentEnvironment?.id}
      onChange={(e) => {
        const newEnv = environments.find(env => env.id === e.target.value);
        if (newEnv) setCurrentEnvironment(newEnv);
      }}
      style={{ minWidth: 120 }}
    >
      {environments.map((env) => (
        <MenuItem key={env.id} value={env.id}>{env.name}</MenuItem>
      ))}
    </Select>
  );
};

export const EnvironmentList = () => (
  <>
    <EnvironmentSelector />
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
  </>
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
