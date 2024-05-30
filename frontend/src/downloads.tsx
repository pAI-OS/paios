import { List, Datagrid, TextField, TextInput, useRecordContext, useNotify, useRefresh, Button } from 'react-admin';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DeleteIcon from '@mui/icons-material/Delete';
import { apiBase, httpClient } from "./apiBackend";

interface Download {
    id: string;
    source_url: string;
    target_file: string;
    target_dir: string;
    total_size: number;
    downloaded: number;
    progress: number;
    status: string;
}

const downloadFilters = [
    <TextInput source="q" label="Search" alwaysOn />,
];

const DownloadActions = () => {
    const record = useRecordContext<Download>();
    const notify = useNotify();
    const refresh = useRefresh();

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
            {record.status === 'downloading' ? (
                <Button label="Pause" onClick={() => handlePauseClick(record.id)}>
                    <PauseIcon />
                </Button>
            ) : (
                <Button label="Resume" onClick={() => handleResumeClick(record.id)}>
                    <PlayArrowIcon />
                </Button>
            )}
            <Button label="Delete" onClick={() => handleDeleteClick(record.id)}>
                <DeleteIcon />
            </Button>
        </div>
    );
};

export const DownloadsList = () => (
    <List filters={downloadFilters}>
        <Datagrid rowClick="edit">
            <TextField source="source_url" />
            <TextField source="target_file" />
            <TextField source="target_dir" />
            <TextField source="total_size" />
            <TextField source="downloaded" />
            <TextField source="progress" />
            <TextField source="status" />
            <DownloadActions />
        </Datagrid>
    </List>
);

export default DownloadsList;
