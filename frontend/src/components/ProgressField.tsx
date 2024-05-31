import React from 'react';
import { useRecordContext } from 'react-admin';

const ProgressField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    if (!record) return null;
    const progress = record[source];
    return <span>{progress.toFixed(2)}%</span>;
};

export default ProgressField;
