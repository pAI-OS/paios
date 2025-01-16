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


// Resource configuration
const resourceConfig = [
  {
    name: "assets",
    list: AssetList,
    create: AssetCreate,
    edit: AssetEdit,
    show: AssetShow,
    icon: DocIcon,
    recordRepresentation: 'name',
  },
  {
    name: "users",
    list: UserList,
    create: UserCreate,
    edit: UserEdit,
    show: UserShow,
    icon: UserIcon,
    recordRepresentation: 'name',
  },
  {
    name: "abilities",
    list: AbilityList,
    show: AbilityShow,
    icon: ExtensionIcon,
    recordRepresentation: 'id',
  },
  {
    name: "resources",
    list: ChannelList,
    show: ChannelShow,
    icon: SyncAltIcon,
    recordRepresentation: 'id',
  },
  {
    name: "downloads",
    list: DownloadsList,
  },
  {
    name: "shares",
    list: ShareList,
    create: ShareCreate,
    edit: ShareEdit,
    show: ShareShow,
    icon: LinkIcon,
    recordRepresentation: 'id',
  },
];

const renderResources: RenderResourcesFunction = (permissions: ResourcePermissions) => (
  <>
    {resourceConfig.map(resource => {
      if (!hasAccess(resource.name, "list", permissions)) return null;

      return (
        <Resource
          key={resource.name}
          name={resource.name}
          list={resource.list}
          create={hasAccess(resource.name, "create", permissions) ? resource.create : undefined}
          edit={hasAccess(resource.name, "edit", permissions) ? resource.edit : undefined}
          show={hasAccess(resource.name, "show", permissions) ? resource.show : undefined}
          icon={resource.icon}
          recordRepresentation={resource.recordRepresentation}
        />
      );
    })}
    <CustomRoutes noLayout>
      <Route path='/verify-email/:token' element={<VerifyEmail />} />
    </CustomRoutes>
  </>
);

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
