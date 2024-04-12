import {
  Admin,
  Resource
} from "react-admin";
import { UserList, UserShow } from "./users";
import { DocList, DocCreate, DocEdit } from "./docs";
import { dataProvider } from "./dataProvider";
import DocIcon from "@mui/icons-material/Book";
import UserIcon from "@mui/icons-material/Group";
import { Dashboard } from "./Dashboard";
import { authProvider } from "./authProvider";

export const App = () => (
<Admin dataProvider={dataProvider} authProvider={authProvider} dashboard={Dashboard} >
  <Resource name="posts" list={DocList} create={DocCreate} edit={DocEdit} icon={DocIcon} />
  <Resource name="users" list={UserList} show={UserShow} recordRepresentation="name" icon={UserIcon} />
</Admin>
);
