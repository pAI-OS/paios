import React from 'react';
import { Admin, CustomRoutes, RenderResourcesFunction, Resource } from 'react-admin';
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
import { hasAccess, ResourcePermissions } from './utils/authUtils';


const renderResources: RenderResourcesFunction = (permissions: ResourcePermissions) => (
  <>
    {hasAccess("assets", "list", permissions) ?
      <Resource
        name="assets"
        list={AssetList}
        create={hasAccess("assets", "create", permissions) ? AssetCreate : undefined}
        edit={hasAccess("assets", "edit", permissions) ? AssetEdit : undefined}
        show={hasAccess("assets", "show", permissions) ? AssetShow : undefined}
        recordRepresentation='name'
        icon={DocIcon} /> : null}
    {hasAccess("users", "list", permissions) ?
      <Resource
        name="users"
        list={UserList}
        create={hasAccess("users", "create", permissions) ? UserCreate : undefined}
        edit={hasAccess("users", "edit", permissions) ? UserEdit : undefined}
        show={hasAccess("users", "show", permissions) ? UserShow : undefined}
        recordRepresentation='name'
        icon={UserIcon} /> : null}
    {hasAccess("abilities", "list", permissions) ?
      <Resource
        name="abilities"
        list={AbilityList}
        show={hasAccess("abilities", "show", permissions) ? AbilityShow : undefined}
        recordRepresentation='id'
        icon={ExtensionIcon} /> : null}
    {hasAccess("resources", "list", permissions) ?
      <Resource
        name="resources"
        list={ChannelList}
        show={hasAccess("abilities", "show", permissions) ? ChannelShow : undefined}
        recordRepresentation='id'
        icon={SyncAltIcon} /> : null}
    {hasAccess("downloads", "list", permissions) ?
      <Resource
        name="downloads"
        list={DownloadsList} /> : null}
    {hasAccess("shares", "list", permissions) ?
      <Resource
        name="shares"
        list={ShareList}
        create={hasAccess("shares", "create", permissions) ? ShareCreate : undefined}
        edit={hasAccess("shares", "edit", permissions) ? ShareEdit : undefined}
        show={hasAccess("shares", "show", permissions) ? ShareShow : undefined}
        recordRepresentation='id'
        icon={LinkIcon} /> : null}
    <CustomRoutes noLayout>
      <Route path='/verify-email/:token' element={<VerifyEmail />} />
    </CustomRoutes>
  </>
)

export const App = () => (
  <Admin
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
    layout={CustomLayout}
    loginPage={Login}
  >
    {renderResources}
  </Admin>
);
