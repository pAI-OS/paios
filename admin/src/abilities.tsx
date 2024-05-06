import { useNotify, useRefresh, useRecordContext, TabbedShowLayout, Tab, UrlField } from "react-admin";
import { Button, List, Datagrid, TextField, WrapperField, Show, SimpleShowLayout, ShowButton } from "react-admin";
import { Link } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import { apiBase, httpClient } from "./apiBackend";
import { DebianDependency } from './dependencies/DebianDependency';
import { PythonDependency } from './dependencies/PythonDependency';
import { ResourceDependency } from './dependencies/ResourceDependency';

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

    const hasStartScript = Boolean(record.scripts?.start);

    return hasStartScript && (isStarted ? (
        <Button label="Stop" onClick={handleStopClick}>
            <StopIcon />
        </Button>
    ) : (
        <Button label="Start" onClick={handleStartClick}>
            <PlayArrowIcon />
        </Button>
    ));
};

const AbilityTitle = () => {
    const record = useRecordContext();
    return <span>Abilities {record ? `- ${record.title} (${record.id})` : ""}</span>;
};

export const AbilityList = () => (
    <List>
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
            <WrapperField label="Ability">
                <TextField source="title" /> (<TextField source="id" />)
            </WrapperField>
            <WrapperField label="Author">
                <Link href="author.url">
                    <TextField source="author.name" />
                </Link>
            </WrapperField>
            <TextField source="description" />
            <AbilityDependencies />
        </SimpleShowLayout>
    </Show>
);

export const AbilityDependencies = () => {
    const record = useRecordContext();

    if (!record) { return null; }
    if (!record.dependencies) { return null; }
    // or any other fallback UI

    const dependencies = record.dependencies;

    return (
        <TabbedShowLayout >
            {dependencies.debian && (<Tab label="Debian"><DebianDependency dependencies={dependencies.debian} /></Tab>)}
            {dependencies.python && (<Tab label="Python"><PythonDependency dependencies={dependencies.python} abilityId={record.id} /></Tab>)}
            {dependencies.resources && (<Tab label="Resource"><ResourceDependency dependencies={dependencies.resources} abilityId={record.id} /></Tab>)}
        </TabbedShowLayout>
    );
};
