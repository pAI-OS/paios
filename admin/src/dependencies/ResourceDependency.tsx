// ResourceDependency.tsx
import { Button, Datagrid, TextField } from 'react-admin';
import DownloadForOfflineIcon from '@mui/icons-material/DownloadForOffline';

export const ResourceDependency = (props: { dependencies: any }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="filename" />
            <TextField source="url" />
            <Button label="Download" onClick={() => { /* handle download action */ }}>
                <DownloadForOfflineIcon />
            </Button>
        </Datagrid>
    );
};
