// PtyhonDependency.tsx
import { Button, Datagrid, TextField } from 'react-admin';
import { CheckedField } from '../lib/CheckedField';
import GetAppIcon from '@mui/icons-material/GetApp';
import { useRecordContext, useNotify, useRefresh } from 'react-admin';
import { apiBase, httpClient } from '../apiBackend';

export const PythonDependency = (props: { dependencies: any }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="id" />
            <TextField source="name" />
            <CheckedField source="installed" />
            <TextField source="version" />
            <CheckedField source="satisfied" />
            <InstallButton />
        </Datagrid>
    );
};

const InstallButton = () => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();
    const abilityId = String(record.abilityId);

    const handleInstallClick = (event: React.MouseEvent) => {
        event.stopPropagation(); // prevent the click event propagating to the row and calling show

        httpClient(`${apiBase}/abilities/${abilityId}/dependencies/python/${record.id}/install`, { method: 'POST' })
            .then(() => {
                notify('Python dependency installation started');
                refresh();
            })
            .catch((e) => {
                notify('Error: Python dependency not installed', { type: 'warning' })
            });
    };

    return (
        <Button label={record.installed ? (record.satisfied ? "Install" : "Upgrade") : "Install"} onClick={handleInstallClick}>
            <GetAppIcon />
        </Button>
    );
};
