import { Layout, AppBar, UserMenu, useLogout } from 'react-admin';
import { EnvironmentSelector } from './environments';
import { MenuItem } from '@mui/material'; // Import MenuItem from MUI instead

const CustomAppBar = () => {
  const logout = useLogout();

  return (
    <AppBar userMenu={
      <UserMenu>
        <MenuItem onClick={() => logout()}>Logout</MenuItem>
      </UserMenu>
    }>
      <EnvironmentSelector />
    </AppBar>
  );
};

export const CustomLayout = (props: any) => <Layout {...props} appBar={CustomAppBar} />;
