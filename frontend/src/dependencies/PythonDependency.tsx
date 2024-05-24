// PythonDependency.tsx
import { Button, Datagrid, TextField } from 'react-admin';
import { useState, useEffect, useRef } from 'react';
import { CheckedField } from '../components/CheckedField';
import GetAppIcon from '@mui/icons-material/GetApp';
import { useRecordContext, useNotify, useRefresh } from 'react-admin';
import { apiBase, httpClient } from '../apiBackend';

export const PythonDependency = (props: { dependencies: any, abilityId: string }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="id" />
            <TextField source="name" />
            <TextField source="version-installed" label="Installed" />
            <TextField source="version" label="Required" />
            <CheckedField source="satisfied" />
            <InstallButton abilityId={props.abilityId} />
        </Datagrid>
    );
};


const InstallButton = ({ abilityId }: { abilityId: string }) => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();
    const [isInstalling, setIsInstalling] = useState(false);
    const intervalId = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        // Clear any existing interval
        if (intervalId.current) {
            clearInterval(intervalId.current);
            intervalId.current = null;
        }

        // Set a new interval if the package is currently installing
        if (isInstalling) {
            intervalId.current = setInterval(() => {
                refresh();
            }, 5000); // Refresh every 5 seconds
        }

        return () => {
            // Clear the interval when the component is unmounted or the installing state changes
            if (intervalId.current) {
                clearInterval(intervalId.current);
            }
        };
    }, [isInstalling, refresh]);

    const handleInstallClick = (event: React.MouseEvent) => {
        event.stopPropagation();
        setIsInstalling(true);

        httpClient(`${apiBase}/abilities/${abilityId}/dependencies/python/${record.id}/install`, { method: 'POST' })
            .then(() => {
                notify('Python dependency installation requested');
                refresh();
            })
            .catch((e) => {
                notify('Error: Python dependency not installed', { type: 'warning' });
            })
            .finally(() => {
                setIsInstalling(false);
            });
    };

    const buttonLabel = isInstalling ? "Installing" : (record.installed ? (record.satisfied ? "Install" : "Upgrade") : "Install");

    return (
        !record.satisfied && (
            <Button label={buttonLabel} onClick={handleInstallClick} disabled={isInstalling}>
                <GetAppIcon />
            </Button>
        )
    );
};
