import { List, SimpleList } from 'react-admin';

export const UserList = () => (
    <List>
        <SimpleList
            primaryText={record => record.name}
            secondaryText={record => record.username}
            tertiaryText={record => record.email}
        />
    </List>
);
