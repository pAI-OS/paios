import { Menu } from "react-admin";
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ApiIcon from '@mui/icons-material/Api';
import { apiBase } from './apiBackend';

export const CustomMenu = () => (
  <Menu>
    <Menu.DashboardItem />
    <Menu.ResourceItem name="assets" />
    <Menu.ResourceItem name="users" />
    <Menu.ResourceItem name="abilities" />
    <Menu.ResourceItem name="resources" />
    <Menu.ResourceItem name="downloads" />
    <MenuItem component="a" href={`${apiBase}/ui`}>
      <ListItemIcon>
        <ApiIcon />
      </ListItemIcon>
      <ListItemText primary="API Docs" />
    </MenuItem>
  </Menu>
);

export default CustomMenu;
