import { useRecordContext } from "react-admin";
import { Edit, Create, List, Datagrid, TextField, TextInput, ReferenceField, ReferenceInput, SimpleForm, EditButton } from "react-admin";

const DocumentTitle = () => {
    const record = useRecordContext();
    return <span>Document {record ? `"${record.title}"` : ""}</span>;
};

const docFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
    <ReferenceInput source="userId" label="User" reference="users" />,
];

export const DocList = () => (
    <List filters={docFilters}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <ReferenceField source="userId" reference="users" link="show" />
            <TextField source="title" />
            <EditButton />
        </Datagrid>
    </List>
);

export const DocEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="id" InputProps={{ disabled: true }}/>
            <ReferenceInput source="userId" reference="users" />
            <TextInput source="title" />
            <TextInput source="body" multiline rows={5} />
        </SimpleForm>
    </Edit>
);

export const DocCreate = () => (
    <Create>
        <SimpleForm>
            <ReferenceInput source="userId" reference="users" />
            <TextInput source="title" />
            <TextInput source="body" multiline rows={5} />
        </SimpleForm>
    </Create>
);
