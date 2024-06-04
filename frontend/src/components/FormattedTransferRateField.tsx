import { useRecordContext } from 'react-admin';
import { formatTransferRate } from '../utils/formatSize';

const FormattedTransferRateField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    if (!record) return null;
    const rate = record[source];
    if (rate === 0) return null;
    return <span>{formatTransferRate(rate)}</span>;
};

export default FormattedTransferRateField;
