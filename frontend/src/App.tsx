import {
  Admin,
  Resource,
  Menu
} from "react-admin";
import { UserList, UserCreate, UserEdit, UserShow } from "./users";
import { AbilityList, AbilityShow } from "./abilities";
import { AssetList, AssetCreate, AssetEdit } from "./assets";
import { ChannelList, ChannelShow } from "./channels";
import { dataProvider } from "./dataProvider";
import DocIcon from "@mui/icons-material/Book";
import UserIcon from "@mui/icons-material/Group";
import ExtensionIcon from '@mui/icons-material/Extension';
import SyncAltIcon from '@mui/icons-material/SyncAlt';
import { Dashboard } from "./Dashboard";
import { authProvider } from "./authProvider";
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ApiIcon from '@mui/icons-material/Api';
import { apiBase } from './apiBackend';

const CustomMenu = () => (
  <Menu>
    <Menu.DashboardItem />
    <Menu.ResourceItem name="assets" />
    <Menu.ResourceItem name="users" />
    <Menu.ResourceItem name="abilities" />
    <Menu.ResourceItem name="channels" />
    <MenuItem component="a" href={`${apiBase}/ui`}>
      <ListItemIcon>
        <ApiIcon />
      </ListItemIcon>
      <ListItemText primary="API Docs" />
    </MenuItem>
  </Menu>
);

export const App = () => (
  <Admin
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
    menu={CustomMenu}
  >
    <Resource name="assets" list={AssetList} create={AssetCreate} edit={AssetEdit} recordRepresentation='title' icon={DocIcon} />
    <Resource name="users" list={UserList} create={UserCreate} edit={UserEdit} show={UserShow} recordRepresentation='name' icon={UserIcon} />
    <Resource name="abilities" list={AbilityList} show={AbilityShow} recordRepresentation='id' icon={ExtensionIcon} />
    <Resource name="channels" list={ChannelList} show={ChannelShow} recordRepresentation='id' icon={SyncAltIcon} />
  </Admin>
);
