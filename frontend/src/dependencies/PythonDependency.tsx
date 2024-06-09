import { Button, Datagrid, TextField } from 'react-admin';
import { useState, useEffect, useRef } from 'react';
import { CheckedField } from '../components/CheckedField';
import GetAppIcon from '@mui/icons-material/GetApp';
import { useRecordContext, useNotify, useRefresh } from 'react-admin';
import { apiBase, httpClient } from '../apiBackend';

export const PythonDependency = (props: { dependencies: any, ability_id: string }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="id" />
            <TextField source="name" />
            <CheckedField source="versions.satisfied" label="Satisfied" />
            <TextField source="versions.required" label="Required" />
            <TextField source="versions.installed" label="Installed" />
            <TextField source="versions.latest" label="Latest" />
            <InstallButton ability_id={props.ability_id} />
        </Datagrid>
    );
};

const InstallButton = ({ ability_id }: { ability_id: string }) => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();
    const [isInstalling, setIsInstalling] = useState(false);
    const intervalId = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (intervalId.current) {
            clearInterval(intervalId.current);
            intervalId.current = null;
        }

        if (isInstalling) {
            intervalId.current = setInterval(() => {
                refresh();
            }, 5000);
        }

        return () => {
            if (intervalId.current) {
                clearInterval(intervalId.current);
            }
        };
    }, [isInstalling, refresh]);

    const handleInstallClick = (event: React.MouseEvent) => {
        event.stopPropagation();
        setIsInstalling(true);

        httpClient(`${apiBase}/abilities/${ability_id}/dependencies/${record.id}/install`, { method: 'POST' })
            .then(() => {
                notify('Python dependency installation requested');
                //refresh();
            })
            .catch((e: any) => {
                notify('Error: Python dependency not installed', { type: 'warning' });
            })
            //.finally(() => {
            //    setIsInstalling(false);
            //});
    };

    const isLatestVersion = record.versions.installed === record.versions.latest;
    const buttonLabel = isInstalling ? "Installing" : (record.versions.installed ? (record.versions.satisfied ? "Install" : "Upgrade") : "Install");

    if (isLatestVersion) {
        return null; // Hide the button if the installed version is the latest version
    }

    return (
        <Button label={buttonLabel} onClick={handleInstallClick} disabled={isInstalling || record.state === 'installing'}>
            <GetAppIcon />
        </Button>
    );
};
