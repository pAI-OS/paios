import { useMediaQuery, Theme } from "@mui/material";
import { Create, Edit, EditButton, DeleteButton, List, SimpleList, Show, ShowButton, SimpleForm, SimpleShowLayout, Datagrid, TextField, TextInput, EmailField, SelectInput, useRecordContext, usePermissions } from "react-admin";
import { hasAccess } from "./utils/authUtils";

const UserTitle = () => {
    const record = useRecordContext();
    return <span>Users {record ? `- ${record.name}` : ""}</span>;
};

const roleChoices = [
    { id: 'user', name: 'User' },
    { id: 'admin', name: 'Admin' },
];

export const UserList = () => {
    const isSmall = useMediaQuery<Theme>((theme) => theme.breakpoints.down("sm"));
    const { permissions } = usePermissions()
    return (
        <List>
            {isSmall ? (
                <SimpleList
                    primaryText={(record) => record.name}
                    secondaryText={(record) => record.email}
                    tertiaryText={(record) => record.role}
                />
            ) : (
                <Datagrid rowClick="edit">
                    <TextField source="name" />
                    <EmailField source="email" />
                    <TextField source="role" />
                    {hasAccess("users", "show", permissions) && <ShowButton />}
                    {hasAccess("users", "edit", permissions) && <EditButton />}
                    {hasAccess("users", "delete", permissions) && <DeleteButton />}
                </Datagrid>
            )}
        </List>
    );
};

export const UserShow = () => (
    <Show title={<UserTitle />}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="name" />
            <EmailField source="email" />
            <TextField source="role" />
        </SimpleShowLayout>
    </Show>
);

export const UserEdit = () => (
    <Edit title={<UserTitle />}>
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="email" />
            <SelectInput source="role" choices={roleChoices} />
        </SimpleForm>
    </Edit>
);

export const UserCreate = () => (
    <Create redirect="show">
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="email" />
            <SelectInput source="role" choices={roleChoices} defaultValue="user" />
        </SimpleForm>
    </Create>
);
