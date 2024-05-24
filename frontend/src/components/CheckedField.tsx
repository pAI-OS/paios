import CheckIcon from '@mui/icons-material/Check';
import CrossIcon from '@mui/icons-material/Clear';

import { useRecordContext } from 'react-admin';

export const CheckedField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    const value = record[source];
    return value ? <CheckIcon /> : <CrossIcon />;
};
