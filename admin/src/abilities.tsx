import { useRecordContext } from "react-admin";
import { List, Datagrid, TextField, TextInput, Show, SimpleShowLayout, EditButton } from "react-admin";

const AbilityTitle = () => {
    const record = useRecordContext();
    return <span>Ability {record ? `"${record.title}"` : ""}</span>;
};

const abilityFilters = [
    <TextInput source="q" label="Search" alwaysOn />
];

export const AbilityList = () => (
    <List filters={abilityFilters}>
        <Datagrid rowClick="edit">
            <TextField source="name" />
            <TextField source="description" />
            <EditButton />
        </Datagrid>
    </List>
);

export const AbilityShow = () => (
    <Show>
        <SimpleShowLayout>
                <TextField source="name" />
                    <TextField source="name" />
                    <TextField source="description" />
        </SimpleShowLayout>
    </Show>
);
