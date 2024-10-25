import React from 'react';
import { Admin, CustomRoutes, Resource } from 'react-admin';
import { Route } from 'react-router-dom';
import { UserList, UserCreate, UserEdit, UserShow } from "./users";
import { AbilityList, AbilityShow } from "./abilities";
import { AssetList, AssetCreate, AssetEdit, AssetShow } from "./assets";
import { ChannelList, ChannelShow } from "./resources";
import { ShareList, ShareCreate, ShareEdit, ShareShow } from "./shares";
import { DownloadsList } from "./downloads";
import { dataProvider } from "./dataProvider";
import DocIcon from "@mui/icons-material/Book";
import UserIcon from "@mui/icons-material/Group";
import ExtensionIcon from '@mui/icons-material/Extension';
import SyncAltIcon from '@mui/icons-material/SyncAlt';
import LinkIcon from '@mui/icons-material/Link';
import { Dashboard } from "./Dashboard";
import { authProvider } from "./authProvider";
import { CustomLayout } from './CustomLayout';
import Login from './Login';
import { VerifyEmail } from './VerifyEmail';

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
    <Resource name="resources" list={ChannelList} show={ChannelShow} recordRepresentation='id' icon={SyncAltIcon} />
    <Resource name="downloads" list={DownloadsList} />
    <Resource name="shares" list={ShareList} create={ShareCreate} edit={ShareEdit} show={ShareShow} recordRepresentation='id' icon={LinkIcon} />
    <CustomRoutes noLayout>
      <Route path='/verify-email/:token' element={<VerifyEmail />} />
    </CustomRoutes>
  </Admin>
);
