import {
  Admin,
  Resource
} from "react-admin";
import { UserList, UserShow } from "./users";
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

export const App = () => (
<Admin dataProvider={dataProvider} authProvider={authProvider} dashboard={Dashboard} >
  <Resource name="assets" list={AssetList} create={AssetCreate} edit={AssetEdit} recordRepresentation='title' icon={DocIcon} />
  <Resource name="users" list={UserList} show={UserShow} recordRepresentation={(record) => `${record.firstName} ${record.lastName}`} icon={UserIcon} />
  <Resource name="abilities" list={AbilityList} show={AbilityShow} recordRepresentation='id' icon={ExtensionIcon} />
  <Resource name="channels" list={ChannelList} show={ChannelShow} recordRepresentation='id' icon={SyncAltIcon} />
</Admin>
);
