import { useMediaQuery, Theme } from "@mui/material";
import { Create, Edit, EditButton, DeleteButton, List, SimpleList, Show, ShowButton, SimpleForm, SimpleShowLayout, Datagrid, TextField, TextInput, EmailField, SelectInput, useRecordContext } from "react-admin";

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
                    <ShowButton />
                    <EditButton />
                    <DeleteButton />
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
