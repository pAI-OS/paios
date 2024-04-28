import { Button, useNotify, useRefresh, useRecordContext } from "react-admin";
import { List, Datagrid, TextField, TextInput, Show, SimpleShowLayout, ShowButton } from "react-admin";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const StartButton = () => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();

    const handleClick = () => {
        // Replace this with your actual start logic
        fetch(`/api/abilities/start/${record.id}`, { method: 'POST' })
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
    return <span>Ability {record ? `"${record.name}"` : ""}</span>;
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
    <Show>
        <SimpleShowLayout>
                <TextField source="id" />
                    <TextField source="title" />
                    <TextField source="description" />
        </SimpleShowLayout>
    </Show>
);
