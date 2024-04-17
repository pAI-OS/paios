import { useMediaQuery, Theme } from "@mui/material";
import { List, SimpleList, Show, SimpleShowLayout, Datagrid, TextField, EmailField, UrlField } from "react-admin";

export const UserList = () => {
    const isSmall = useMediaQuery<Theme>((theme) => theme.breakpoints.down("sm"));
    return (
        <List>
            {isSmall ? (
                <SimpleList
                    primaryText={(record) => record.firstName}
                    secondaryText={(record) => record.lastName}
                    tertiaryText={(record) => record.email}
                />
            ) : (
                <Datagrid rowClick="show">
                    <TextField source="id" />
                    <TextField source="firstName" />
                    <TextField source="lastName" />
                    <EmailField source="email" />
                </Datagrid>
            )}
        </List>
    );
};

export const UserShow = () => (
    <Show>
        <SimpleShowLayout>
                <TextField source="id" />
                    <TextField source="firstName" />
                    <TextField source="lastName" />
                    <EmailField source="email" />
        </SimpleShowLayout>
    </Show>
);
