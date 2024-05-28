import { useMediaQuery, Theme } from "@mui/material";
import { List, SimpleList, Show, SimpleShowLayout, Datagrid, TextField, EmailField, useRecordContext } from "react-admin";

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
                <Datagrid rowClick="show">
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
