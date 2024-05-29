import { useMediaQuery, Theme } from "@mui/material";
import { Create, Edit, List, SimpleList, Show, SimpleForm, SimpleShowLayout, Datagrid, TextField, TextInput, ReferenceInput, EmailField, useRecordContext } from "react-admin";

const UserTitle = () => {
    const record = useRecordContext();
    return <span>Users {record ? `- ${record.name}` : ""}</span>;
};

export const UserList = () => {
    const isSmall = useMediaQuery<Theme>((theme) => theme.breakpoints.down("sm"));
    return (
        <List>
            {isSmall ? (
                <SimpleList
                    primaryText={(record) => record.name}
                    secondaryText={(record) => record.email}
                />
            ) : (
                <Datagrid rowClick="edit">
                    <TextField source="name" />
                    <EmailField source="email" />
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
    <Create>
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="email" />
        </SimpleForm>
    </Create>
);
