import { useRecordContext } from "react-admin";
import { List, Datagrid, TextField, TextInput, Show, SimpleShowLayout, ShowButton } from "react-admin";

const AbilityTitle = () => {
    const record = useRecordContext();
    return <span>Ability {record ? `"${record.name}"` : ""}</span>;
};

const abilityFilters = [
    <TextInput source="q" label="Search" alwaysOn />
];

export const AbilityList = () => (
    <List filters={abilityFilters}>
        <Datagrid rowClick="show">
            <TextField source="title" />
            <TextField source="description" />
            <ShowButton />
        </Datagrid>
    </List>
);

export const AbilityShow = () => (
    <Show>
        <SimpleShowLayout>
                <TextField source="id" />
                    <TextField source="title" />
                    <TextField source="description" />
        </SimpleShowLayout>
    </Show>
);
