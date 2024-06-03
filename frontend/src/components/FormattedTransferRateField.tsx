import { useRecordContext } from 'react-admin';
import { formatTransferRate } from '../utils/formatSize';

const FormattedTransferRateField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    if (!record) return null;
    const size = record[source];
    return <span>{formatTransferRate(size)}</span>;
};

export default FormattedTransferRateField;
