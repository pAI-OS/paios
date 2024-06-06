import React, { useState } from 'react';
import { Button, Datagrid, TextField, useRecordContext, useNotify, useRefresh } from 'react-admin';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import { apiBase, httpClient } from "../apiBackend";
import { useNavigate } from 'react-router-dom';

const DownloadButton = ({ ability_id }: { ability_id: string }) => {
    const record = useRecordContext();
    const notify = useNotify();
    const refresh = useRefresh();
    const navigate = useNavigate();
    const [isDownloading, setIsDownloading] = useState(false);

    const handleDownloadClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();
        setIsDownloading(true);

        const downloadData = [
            {
                source_url: record.source_url,
                file_name: record.file_name,
                file_hash: record.file_hash,
                target_directory: `abilities/${ability_id}/resources`
            }
        ];

        httpClient(`${apiBase}/downloads`, { 
            method: 'POST', 
            body: JSON.stringify(downloadData) 
        })
            .then(() => {
                notify('Download started');
                refresh();
                navigate('/downloads'); // Redirect to the downloads page
            })
            .catch((e) => {
                notify(e.body.message, { type: 'warning' });
                setIsDownloading(false);
            });
    };

    const handleDeleteClick = (event: React.MouseEvent) => {
        // prevent the click event propagating to the row and calling show
        event.stopPropagation();

        httpClient(`${apiBase}/abilities/${ability_id}/dependencies/${record.id}/download/delete`, { method: 'POST' })
            .then(() => {
                notify('Download deletion requested');
                refresh();
            })
            .catch((e) => {
                notify(e.body.message, { type: 'warning' });
            });
    };

    // file is downloaded, show delete button
    if ((record.localSize || 0) === (record.file_size || 0)) {
        return (
            <Button label="Delete" onClick={handleDeleteClick}>
                <DeleteIcon />
            </Button>
        );
    }

    // file is not downloaded, show download button
    return (
        <Button label="Download" onClick={handleDownloadClick} disabled={isDownloading}>
            <DownloadIcon />
        </Button>
    );
};

export const ResourceDependency = (props: { dependencies: any }) => {
    const record = useRecordContext();
    const ability_id = String(record.id);

    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="file_name" />
            <TextField source="source_url" />
            <DownloadButton ability_id={ability_id} />
        </Datagrid>
    );
};
