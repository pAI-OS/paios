import { useRecordContext } from "react-admin";
import { Edit, Create, List, Datagrid, TextField, TextInput, ReferenceField, ReferenceInput, SimpleForm, EditButton } from "react-admin";

const AssetTitle = () => {
    const record = useRecordContext();
    return <span>Asset {record ? `"${record.title}"` : ""}</span>;
};

const assetFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
    <ReferenceInput source="userId" label="User" reference="users" />,
];

export const AssetList = () => (
    <List filters={assetFilters}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <ReferenceField source="userId" reference="users" link="show" emptyText="WAT?" />
            <TextField source="title" />
            <EditButton />
        </Datagrid>
    </List>
);

export const AssetEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="id" InputProps={{ disabled: true }}/>
            <ReferenceInput source="userId" reference="users" />
            <TextInput source="title" />
            <TextInput source="description" multiline rows={5} />
        </SimpleForm>
    </Edit>
);

export const AssetCreate = () => (
    <Create>
        <SimpleForm>
            <ReferenceInput source="userId" reference="users" />
            <TextInput source="title" />
            <TextInput source="description" multiline rows={5} />
        </SimpleForm>
    </Create>
);
