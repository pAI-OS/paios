import React from 'react';
import { Admin, Resource } from 'react-admin';
import { UserList, UserCreate, UserEdit, UserShow } from "./users";
import { AbilityList, AbilityShow } from "./abilities";
import { AssetList, AssetCreate, AssetEdit, AssetShow } from "./assets";
import { ChannelList, ChannelShow } from "./channels";
import { DownloadsList } from "./downloads";
import { dataProvider } from "./dataProvider";
import DocIcon from "@mui/icons-material/Book";
import UserIcon from "@mui/icons-material/Group";
import ExtensionIcon from '@mui/icons-material/Extension';
import SyncAltIcon from '@mui/icons-material/SyncAlt';
import { Dashboard } from "./Dashboard";
import { authProvider } from "./authProvider";
import { CustomLayout } from './CustomLayout';
import Login from './Login';

export const App = () => (
  <Admin
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
    layout={CustomLayout}
    loginPage={Login}
  >
    <Resource name="assets" list={AssetList} create={AssetCreate} edit={AssetEdit} show={AssetShow} recordRepresentation='name' icon={DocIcon} />
    <Resource name="users" list={UserList} create={UserCreate} edit={UserEdit} show={UserShow} recordRepresentation='name' icon={UserIcon} />
    <Resource name="abilities" list={AbilityList} show={AbilityShow} recordRepresentation='id' icon={ExtensionIcon} />
    <Resource name="channels" list={ChannelList} show={ChannelShow} recordRepresentation='id' icon={SyncAltIcon} />
    <Resource name="downloads" list={DownloadsList} />
  </Admin>
);
