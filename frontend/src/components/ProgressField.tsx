import { useRecordContext } from 'react-admin';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';

const LinearProgressWithLabel = ({ value }: { value: number }) => {
    return (
        <div style={{ display: 'flex', alignItems: 'center' }}>
            <LinearProgress variant="determinate" value={value} style={{ width: '80%' }} />
            <Typography variant="body2" style={{ marginLeft: 10 }}>{`${Math.round(value)}%`}</Typography>
        </div>
    );
};

const ProgressField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    if (!record) return null;
    const progress = record[source];

    return (
        <div style={{ width: '100%' }}>
            <LinearProgressWithLabel value={progress} />
        </div>
    );
};

export default ProgressField;
