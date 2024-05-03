// ResourceDependency.tsx
import { Button, Datagrid, TextField, useRecordContext, useNotify, useRefresh } from 'react-admin';
import DownloadForOfflineIcon from '@mui/icons-material/DownloadForOffline';
import FileDownloadOffIcon from '@mui/icons-material/FileDownloadOff';
import DeleteIcon from '@mui/icons-material/Delete'
import { apiBase, httpClient } from "../apiBackend";

const DownloadButton = ({ abilityId }: { abilityId: string }) => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();
    const isDownloaded = false;

    const handleDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${abilityId}/dependencies/resources/${record.id}/download`, { method: 'POST' })
            .then(() => {
                notify('Download started');
                refresh();
            })
            .catch((e) => {
                notify('Error: download not started', { type: 'warning' })
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

    return !isDownloaded ? (
        <Button label="Download" onClick={handleDownloadClick}>
            <DownloadForOfflineIcon />
        </Button>
    ) : (
        <Button label="Start" onClick={handleStopClick}>
            <FileDownloadOffIcon />
        </Button>
    );
};

export const ResourceDependency = (props: { dependencies: any }) => {
    const record = useRecordContext();
    const abilityId = record.id;

    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="filename" />
            <TextField source="url" />
            <DownloadButton abilityId={abilityId} />        
        </Datagrid>
    );
};
