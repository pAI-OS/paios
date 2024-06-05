import { useNotify, useRefresh, useRecordContext, TabbedShowLayout, Tab } from "react-admin";
import { Button, List, Datagrid, TextField, WrapperField, Show, SimpleShowLayout, ShowButton, TextInput } from "react-admin";
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
    return <span>Abilities {record ? `- ${record.name} (${record.id})` : ""}</span>;
};

const abilityFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
];

export const AbilityList = () => (
    <List filters={abilityFilters}>
        <Datagrid rowClick="show">
            <TextField source="id" label="Name" />
            <TextField source="name" />
            <TextField source="description" />
            <TextField source="versions.package" label="Package Version" />
            <TextField source="versions.product" label="Product Version" />
            <StartStopButton />
            <ShowButton />
        </Datagrid>
    </List>
);

export const AbilityShow = () => (
    <Show title={<AbilityTitle />}>
        <SimpleShowLayout>
            <WrapperField label="Ability">
                <TextField source="name" /> (<TextField source="id" />)
            </WrapperField>
            <WrapperField label="Author">
                <TextField source="author.name" />
            </WrapperField>
            <TextField source="description" />
            <TextField source="versions.package" label="Package Version" />
            <TextField source="versions.product" label="Product Version" />
            <WrapperField label="Dependencies">
                <AbilityDependencies />
            </WrapperField>
        </SimpleShowLayout>
    </Show>
);

interface Dependency {
    type: 'abilities' | 'container' | 'linux' | 'python' | 'resources';
    name?: string;
    description?: string;
    version?: string;
    priority?: string;
    extras?: string[];
    source_url?: string;
    file_name?: string;
    file_size?: number;
    file_hash?: string;
    hash_type?: string;
    packages?: object[];
}

export const AbilityDependencies = () => {
    const record = useRecordContext();

    if (!record) { return null; }
    if (!record.dependencies) { return null; }

    const dependencies: Dependency[] = Array.isArray(record.dependencies) ? record.dependencies : [];

    const debianDeps = dependencies.filter((dep: Dependency) => dep.type === 'linux');
    const pythonDeps = dependencies.filter((dep: Dependency) => dep.type === 'python');
    const resourceDeps = dependencies.filter((dep: Dependency) => dep.type === 'resources');

    return (
        <TabbedShowLayout>
            {debianDeps.length > 0 && (<Tab label="Debian"><DebianDependency dependencies={debianDeps} /></Tab>)}
            {pythonDeps.length > 0 && (<Tab label="Python"><PythonDependency dependencies={pythonDeps} ability_id={String(record.id)} /></Tab>)}
            {resourceDeps.length > 0 && (<Tab label="Resource"><ResourceDependency dependencies={resourceDeps} /></Tab>)}
        </TabbedShowLayout>
    );
};
