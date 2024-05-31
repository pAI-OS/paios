import React from 'react';
import { useRecordContext } from 'react-admin';
import { formatSize } from '../utils/formatSize';

const FormattedSizeField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    if (!record) return null;
    const size = record[source];
    return <span>{formatSize(size)}</span>;
};

export default FormattedSizeField;
