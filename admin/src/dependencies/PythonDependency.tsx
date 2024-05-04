// PtyhonDependency.tsx
import { Datagrid, TextField } from 'react-admin';
import { CheckedField } from '../lib/CheckedField';

export const PythonDependency = (props: { dependencies: any }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="id" />
            <TextField source="name" />
            <CheckedField source="installed" />
            <TextField source="version" />
            <CheckedField source="satisfied" />
        </Datagrid>
    );
};
