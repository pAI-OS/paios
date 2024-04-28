import { Button, useNotify, useRefresh, useRecordContext } from "react-admin";
import { List, Datagrid, TextField, TextInput, Show, SimpleShowLayout, ShowButton } from "react-admin";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { apiBase, httpClient } from "./apiBackend";

const StartButton = () => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();

    const handleClick = () => {
        httpClient(`${apiBase}/abilities/${record.id}/start`, { method: 'POST' })
            .then(() => {
                notify('Ability started');
                refresh();
            })
            .catch((e) => {
                notify('Error: ability not started', { type: 'warning' })
            });
    };

    return (
        <Button label="Start" onClick={handleClick}>
            <PlayArrowIcon />
        </Button>
    );
};

const AbilityTitle = () => {
    const record = useRecordContext();
    return <span>Abilities {record ? `- ${record.id}` : ""}</span>;
};

const abilityFilters = [
    <TextInput source="q" label="Search" alwaysOn />
];

export const AbilityList = () => (
    <List filters={abilityFilters}>
        <Datagrid rowClick="show">
            <TextField source="id" label="Name" />
            <TextField source="title" />
            <TextField source="description" />
            <StartButton />
            <ShowButton />
        </Datagrid>
    </List>
);

export const AbilityShow = () => (
    <Show title={<AbilityTitle />}>
            <SimpleShowLayout>
                <TextField source="id" />
                <TextField source="title" />
                <TextField source="description" />
            </SimpleShowLayout>
        </Show>
    );
