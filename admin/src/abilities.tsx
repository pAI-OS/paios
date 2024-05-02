import { useNotify, useRefresh, useRecordContext } from "react-admin";
import { Button, List, Datagrid, UrlField, TextField, TextInput, Show, SimpleShowLayout, ShowButton } from "react-admin";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import { apiBase, httpClient } from "./apiBackend";

const StartStopButton = () => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();
    const isStarted = Boolean(record.pid);

    const handleStartClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${record.id}/start`, { method: 'POST' })
            .then(() => {
                notify('Ability started');
                refresh();
            })
            .catch((e) => {
                notify('Error: ability not started', { type: 'warning' })
            });
    };

    const handleStopClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${record.id}/stop`, { method: 'POST' })
            .then(() => {
                notify('Ability stopped');
                refresh();
            })
            .catch((e) => {
                notify('Error: ability not stopped', { type: 'warning' })
            });
    };

    return isStarted ? (
        <Button label="Stop" onClick={handleStopClick}>
            <StopIcon />
        </Button>
    ) : (
        <Button label="Start" onClick={handleStartClick}>
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
            <StartStopButton />
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
                <AbilityDependencies />
            </SimpleShowLayout>
        </Show>
    );

export const AbilityDependencies = () => {
    const record = useRecordContext();

    if (!record) {
        console.log("Record not available");
        return null; // or any other fallback UI
    }
    console.log("Record: ");
    console.log(record);

    const dependencies = record.dependencies;
    console.log("Dependencies: ");
    console.log(dependencies);

    //const dependencies = record.dependencies.resources;
    const resources = dependencies.resources;
    console.log("Resources: ");
    console.log(resources);

    //const data = resources.map((resource: any) => ({ name: resource.name }));

    return (
        <Datagrid data={resources} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="filename" />
            <UrlField source="url" />
        </Datagrid>
    );
};
