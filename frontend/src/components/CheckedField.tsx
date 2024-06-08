import CheckIcon from '@mui/icons-material/Check';
import CrossIcon from '@mui/icons-material/Clear';
import { useRecordContext, FieldProps } from 'react-admin';

const getNestedValue = (obj: any, path: string) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
};

interface CheckedFieldProps extends FieldProps {
    source: string;
    label?: string;
}

export const CheckedField = ({ source }: CheckedFieldProps) => {
    const record = useRecordContext();
    const value = getNestedValue(record, source);
    return value ? <CheckIcon /> : <CrossIcon />;
};
