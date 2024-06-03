import { useEffect, useRef, useState } from 'react';
import { List, Datagrid, TextField, TextInput, useRecordContext, useNotify, useRefresh, Button } from 'react-admin';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DeleteIcon from '@mui/icons-material/Delete';
import { apiBase, httpClient } from "./apiBackend";
import FormattedSizeField from './components/FormattedSizeField';
import FormattedTransferRateField from './components/FormattedTransferRateField';
import ProgressField from './components/ProgressField';

interface Download {
    download_id: string;
    source_url: string;
    target_filename: string;
    target_directory: string;
    total_size: number;
    downloaded: number;
    progress: number;
    status: string;
}

const downloadFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
];

const DownloadActions = ({ refresh }: { refresh: () => void }) => {
    const record = useRecordContext<Download>();
    const notify = useNotify();

    const handlePauseClick = (id: string) => {
        httpClient(`${apiBase}/downloads/${encodeURIComponent(id)}/pause`, { method: 'POST' })
            .then(() => {
                notify('Download paused');
                refresh();
            })
            .catch(() => notify('Error: could not pause download', { type: 'warning' }));
    };

    const handleResumeClick = (id: string) => {
        httpClient(`${apiBase}/downloads/${encodeURIComponent(id)}/resume`, { method: 'POST' })
            .then(() => {
                notify('Download resumed');
                refresh();
            })
            .catch(() => notify('Error: could not resume download', { type: 'warning' }));
    };

    const handleDeleteClick = (id: string) => {
        httpClient(`${apiBase}/downloads/${encodeURIComponent(id)}`, { method: 'DELETE' })
            .then(() => {
                notify('Download deleted');
                refresh();
            })
            .catch(() => notify('Error: could not delete download', { type: 'warning' }));
    };

    return (
        <div>
            {record.status === 'downloading' && (
                <Button label="Pause" onClick={() => handlePauseClick(record.download_id)}>
                    <PauseIcon />
                </Button>
            )}
            {record.status === 'paused' && (
                <Button label="Resume" onClick={() => handleResumeClick(record.download_id)}>
                    <PlayArrowIcon />
                </Button>
            )}
            <Button label="Delete" onClick={() => handleDeleteClick(record.download_id)}>
                <DeleteIcon />
            </Button>
        </div>
    );
};

export const DownloadsList = () => {
    const refresh = useRefresh();
    const notify = useNotify();
    const intervalId = useRef<NodeJS.Timeout | null>(null);
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
        const refreshWithErrorHandling = async () => {
            try {
                await refresh();
            } catch (error) {
                notify('Error: could not refresh downloads', { type: 'warning' });
                setHasError(true);
            }
        };

        if (!hasError) {
            intervalId.current = setInterval(() => {
                refreshWithErrorHandling();
            }, 5000);
        }

        return () => {
            if (intervalId.current) {
                clearInterval(intervalId.current);
            }
        };
    }, [refresh, hasError, notify]);

    return (
        <List filters={downloadFilters}>
            <Datagrid rowClick="edit">
                <TextField source="source_url" />
                <TextField source="target_filename" />
                <TextField source="target_directory" />
                <FormattedSizeField source="downloaded" />
                <FormattedSizeField source="total_size" />
                <FormattedTransferRateField source="transfer_rate" />
                <ProgressField source="progress" />
                <TextField source="status" />
                <DownloadActions refresh={refresh} />
            </Datagrid>
        </List>
    );
};

export default DownloadsList;
