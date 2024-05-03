// ResourceDependency.tsx
import { Button, Datagrid, TextField, useRecordContext, useNotify, useRefresh } from 'react-admin';
import DownloadIcon from '@mui/icons-material/Download';
import DownloadingIcon from '@mui/icons-material/Downloading';
import FileDownloadOffIcon from '@mui/icons-material/FileDownloadOff';
import DeleteIcon from '@mui/icons-material/Delete'
import { apiBase, httpClient } from "../apiBackend";

const DownloadButton = ({ abilityId }: { abilityId: string }) => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();

    const handleStartDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${abilityId}/dependencies/resources/${record.id}/download/start`, { method: 'POST' })
            .then(() => {
                notify('Download started');
                refresh();
            })
            .catch((e) => {
                notify('Error: download not started', { type: 'warning' })
            });
    };


    const handleStopDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${abilityId}/dependencies/resources/${record.id}/download/start`, { method: 'POST' })
            .then(() => {
                notify('Download started');
                refresh();
            })
            .catch((e) => {
                notify('Error: download not started', { type: 'warning' })
            });
    };


    const handleDeleteDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${abilityId}/dependencies/resources/${record.id}/download/delete`, { method: 'POST' })
            .then(() => {
                notify('Deletion requested');
                refresh();
            })
            .catch((e) => {
                notify('Error: deletion not requested', { type: 'warning' })
            });
    };


    // file is downloaded, show delete button
    if ((record.localSize || 0) === (record.remoteSize || 0)) {
        return (
        <Button label="Delete" onClick={handleDeleteDownloadClick}>
            <DeleteIcon />
        </Button>
        );
    }

    // file is partially downloaded, show continue button
    //if (((record.localSize || 0) > 0) && ((record.localSize || 0) < (record.remoteSize || 0))) {
    if (record.keepDownloading) {
        return (
        <Button label="Downloading" onClick={handleStopDownloadClick}>
            <DownloadingIcon />
        </Button>
        );
    }

    // file is not downloaded, show download button
    if ((record.localSize || 0) === 0) {
        return (
        <Button label="Download" onClick={handleStartDownloadClick}>
            <DownloadIcon />
        </Button>
        );
    }
};

export const ResourceDependency = (props: { dependencies: any }) => {
    const record = useRecordContext();
    const abilityId = String(record.id);

    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="filename" />
            <TextField source="url" />
            <DownloadButton abilityId={abilityId} />        
        </Datagrid>
    );
};
