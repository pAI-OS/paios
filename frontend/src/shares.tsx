import { useRecordContext } from "react-admin";
import { Create, Edit, List, Show, SimpleForm, SimpleShowLayout, Datagrid, TextField, TextInput, DateField, DateTimeInput, BooleanField, BooleanInput, ReferenceField, ReferenceInput, SelectInput } from "react-admin";

const ShareTitle = () => {
    const record = useRecordContext();
    return <span>Shares {record ? `- ${record.name}` : ""}</span>;
};

const shareFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
    <ReferenceInput source="resource_id" label="Resource" reference="resources">
        <SelectInput optionText="name" />
    </ReferenceInput>,
    <ReferenceInput source="user_id" label="User" reference="users" />,
];

export const ShareList = () => (
    <List filters={shareFilters}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <ReferenceField source="resource_id" reference="resources" link="show">
                <TextField source="name" />
            </ReferenceField>
            <ReferenceField source="user_id" reference="users">
                <TextField source="name" />
            </ReferenceField>
            <BooleanField source="is_revoked" />
        </Datagrid>
    </List>
);

export const ShareShow = () => (
    <Show title={<ShareTitle />}>
        <SimpleShowLayout>
            <TextField source="id" />
            <ReferenceField source="resource_id" reference="resources" link="show">
                <TextField source="name" />
            </ReferenceField>
            <ReferenceField source="user_id" reference="users">
                <TextField source="name" />
            </ReferenceField>
            <DateField source="expiration_dt" showTime locales="UTC" />
            <BooleanField source="is_revoked" />
        </SimpleShowLayout>
    </Show>
);

export const ShareEdit = () => (
    <Edit title={<ShareTitle />}>
        <SimpleForm>
            <ReferenceInput source="resource_id" label="Resource" reference="resources">
                <SelectInput optionText="name" />
            </ReferenceInput>
            <ReferenceInput source="user_id" label="User" reference="users">
                <SelectInput optionText="name" />
            </ReferenceInput>
            <DateTimeInput source="expiration_dt" />
            <BooleanInput source="is_revoked" />
        </SimpleForm>
    </Edit>
);

export const ShareCreate = () => (
    <Create redirect="show">
        <SimpleForm>
            <ReferenceInput source="resource_id" label="Resource" reference="resources">
                <SelectInput optionText="name" />
            </ReferenceInput>
            <ReferenceInput source="user_id" label="User" reference="users">
                <SelectInput optionText="name" />
            </ReferenceInput>
            <DateTimeInput source="expiration_dt" />
        </SimpleForm>
    </Create>
);
