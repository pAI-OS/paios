import {
  Admin,
  Resource
} from "react-admin";
import { UserList } from "./users";
import { dataProvider } from "./dataProvider";

export const App = () => (
<Admin dataProvider={dataProvider}>
  <Resource name="users" list={UserList} />
</Admin>
);
