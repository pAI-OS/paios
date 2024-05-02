// ResourceDependency.tsx
import { Datagrid, TextField } from 'react-admin';

export const ResourceDependency = (props: { dependencies: any }) => {
    return (
        <Datagrid data={props.dependencies} sort={{ field: 'name', order: 'ASC' }}>
            <TextField source="name" />
            <TextField source="filename" />
            <TextField source="url" />
        </Datagrid>
    );
};
