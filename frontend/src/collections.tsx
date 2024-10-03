import { useRecordContext } from "react-admin";
import { Edit, Create, List, Show, ShowButton, DeleteButton, SimpleShowLayout, Datagrid, TextField, TextInput, ReferenceField, ReferenceInput, SimpleForm, EditButton } from "react-admin";

const CollectionTitle = () => {
    const record = useRecordContext();
    return <span>Collection {record ? `- ${record.name}` : ""}</span>;
};

const collectionFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
];

export const CollectionList = () => (
    <List filters={collectionFilters}>
        <Datagrid rowClick="show">
            <TextField source="name" />
            <TextField source="description" />
            <ShowButton />
            <EditButton />
            <DeleteButton />
        </Datagrid>
    </List>
);

export const CollectionShow = () => (
    <Show title={<CollectionTitle />}>
        <SimpleShowLayout>
            <TextField source="name" />
            <TextField source="description" />
        </SimpleShowLayout>
    </Show>
);

export const CollectionEdit = () => (
    <Edit title={<CollectionTitle />}>
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="description" multiline rows={5} />
        </SimpleForm>
    </Edit>
);

export const CollectionCreate = () => (
    <Create redirect="show">
        <SimpleForm>
            <TextInput source="name" />
            <TextInput source="description" multiline rows={5} />
        </SimpleForm>
    </Create>
);
