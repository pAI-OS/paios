import React from 'react';
import { useRecordContext } from 'react-admin';

const FormattedSizeField = ({ source }: { source: string }) => {
    const record = useRecordContext();
    if (!record) return null;

    const value = record[source];
    if (value == null) return null; // Handle undefined or null values

    const formattedValue = (value / (1024 * 1024)).toFixed(2); // Assuming value is in bytes and converting to MB

    return <span>{formattedValue} MB</span>;
};

export default FormattedSizeField;
