import {
  Admin,
  Resource
} from "react-admin";
import { UserList, UserShow } from "./users";
import { PostList, PostCreate, PostEdit } from "./posts";
import { dataProvider } from "./dataProvider";
import PostIcon from "@mui/icons-material/Book";
import UserIcon from "@mui/icons-material/Group";
import { Dashboard } from "./Dashboard";

export const App = () => (
<Admin dataProvider={dataProvider} dashboard={Dashboard} >
  <Resource name="posts" list={PostList} create={PostCreate} edit={PostEdit} icon={PostIcon} />
  <Resource name="users" list={UserList} show={UserShow} recordRepresentation="name" icon={UserIcon} />
</Admin>
);
