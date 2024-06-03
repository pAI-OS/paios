// ResourceDependency.tsx
import { useEffect, useRef } from 'react';
import { Button, Datagrid, TextField, useRecordContext, useNotify, useRefresh } from 'react-admin';
import DownloadIcon from '@mui/icons-material/Download';
import DownloadingIcon from '@mui/icons-material/Downloading';
import DeleteIcon from '@mui/icons-material/Delete'
import { apiBase, httpClient } from "../apiBackend";

const DownloadButton = ({ ability_id }: { ability_id: string }) => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();

    const handleStartDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${ability_id}/dependencies/resources/${record.id}/download/start`, { method: 'POST' })
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

        httpClient(`${apiBase}/abilities/${ability_id}/dependencies/resources/${record.id}/download/stop`, { method: 'POST' })
            .then(() => {
                notify('Download stop requested');
                refresh();
            })
            .catch((e) => {
                notify('Error: download not stopped', { type: 'warning' })
            });
    };


    const handleDeleteDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${ability_id}/dependencies/resources/${record.id}/download/delete`, { method: 'POST' })
            .then(() => {
                notify('Download deletion requested');
                refresh();
            })
            .catch((e) => {
                notify('Error: deletion not requested', { type: 'warning' })
            });
    };


    // file is downloaded, show delete button
    if ((record.localSize || 0) === (record.file_size || 0)) {
        return (
        <Button label="Delete" onClick={handleDeleteDownloadClick}>
            <DeleteIcon />
        </Button>
        );
    }

    // file is partially downloaded, show stop button
    if (record.keepDownloading) {
        return (
        <Button label="Downloading" onClick={handleStopDownloadClick}>
            <DownloadingIcon />
        </Button>
        );
    }

    // file is not downloaded, show download button
    //if ((record.localSize || 0) === 0) {
        return (
        <Button label="Download" onClick={handleStartDownloadClick}>
            <DownloadIcon />
        </Button>
        );
    //}
};

export const ResourceDependency = (props: { dependencies: any }) => {
    const record = useRecordContext();
    const refresh = useRefresh();
    const ability_id = String(record.id);
    const intervalId = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        // Clear any existing interval
        if (intervalId.current) {
            clearInterval(intervalId.current);
            intervalId.current = null;
        }

        // If any dependency is still downloading, set a new interval
        if (props.dependencies.some((dependency: any) => dependency.keepDownloading)) {
            intervalId.current = setInterval(() => {
                refresh();
            }, 5000);
        }

        return () => {
            // Clear the interval when the component is unmounted
            if (intervalId.current) {
                clearInterval(intervalId.current);
            }
        };
    }, [props.dependencies, refresh]);

    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="file_name" />
            <TextField source="source_url" />
            <DownloadButton ability_id={ability_id} />    
        </Datagrid>
    );
};
