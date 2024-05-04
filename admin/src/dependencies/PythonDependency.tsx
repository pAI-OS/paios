// PtyhonDependency.tsx
import { Datagrid, TextField } from 'react-admin';

export const PythonDependency = (props: { dependencies: any }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="version" />
        </Datagrid>
    );
};
