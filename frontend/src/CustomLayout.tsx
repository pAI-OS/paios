import React from 'react';
import { Layout, AppBar, UserMenu, useLogout } from 'react-admin';
import { MenuItem, Select } from '@mui/material';
import { useEnvironment } from './EnvironmentContext';

const CustomAppBar = () => {
  const logout = useLogout();
  const { currentEnvironment, setCurrentEnvironment, environments, loading } = useEnvironment();

  if (loading) {
    return <AppBar userMenu={<UserMenu><MenuItem onClick={() => logout()}>Logout</MenuItem></UserMenu>} />;
  }

  return (
    <AppBar userMenu={
      <UserMenu>
        <MenuItem onClick={() => logout()}>Logout</MenuItem>
      </UserMenu>
    }>
      <Select
        value={currentEnvironment.id}
        onChange={(e) => {
          const newEnv = environments.find(env => env.id === e.target.value);
          if (newEnv) setCurrentEnvironment(newEnv);
        }}
        style={{ color: 'white', marginLeft: '1em' }}
      >
        {environments.map((env) => (
          <MenuItem key={env.id} value={env.id}>{env.name}</MenuItem>
        ))}
      </Select>
    </AppBar>
  );
};

export const CustomLayout = (props: any) => <Layout {...props} appBar={CustomAppBar} />;
