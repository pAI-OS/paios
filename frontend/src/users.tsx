import { useMediaQuery, Theme } from "@mui/material";
import { Create, Edit, EditButton, DeleteButton, List, SimpleList, Show, ShowButton, SimpleForm, SimpleShowLayout, Datagrid, TextField, TextInput, EmailField, useRecordContext } from "react-admin";

const UserTitle = () => {
    const record = useRecordContext();
    return <span>Users {record ? `- ${record.name}` : ""}</span>;
};

interface UserRecord {
    id: string;
    name: string;
    email: string;
}

export const UserList = () => {
    const isSmall = useMediaQuery<Theme>((theme) => theme.breakpoints.down("sm"));
    return (
        <List>
            {isSmall ? (
                <SimpleList
                    primaryText={(record: UserRecord) => record.name}
                    secondaryText={(record: UserRecord) => record.email}
                />
            ) : (
                <Datagrid rowClick="edit">
                    <TextField source="name" />
                    <EmailField source="email" />
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
        </SimpleShowLayout>
    </Show>
);

export const UserEdit = () => (
    <Edit title={<UserTitle />}>
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="email" />
        </SimpleForm>
    </Edit>
);

export const UserCreate = () => (
    <Create redirect="show">
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="email" />
        </SimpleForm>
    </Create>
);
