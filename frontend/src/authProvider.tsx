import { AuthProvider } from "react-admin";
import { login, register } from "./apis/auth";
import Cookies from "js-cookie"

export const authProvider: AuthProvider = {
    // called when the user attempts to log in
    login: async ({ email, isRegistering }) => {
        try {
            if (isRegistering) {
                await register(email)
            } else {
                await login(email)
            }
            return Promise.resolve()
        } catch (e) {
            return Promise.reject(e)
        }
    },
    // called when the user clicks on the logout button
    logout: () => {
        Cookies.remove("user")
        return Promise.resolve();
    },
    // called when the API returns an error
    checkError: ({ status }: { status: number }) => {
        if (status === 401 || status === 403) {
            localStorage.removeItem("username");
            return Promise.reject();
        }
        return Promise.resolve();
    },
    // called when the user navigates to a new location, to check for authentication
    checkAuth: () => {
        return Cookies.get("user")
            ? Promise.resolve()
            : Promise.reject();
    },
    // called when the user navigates to a new location, to check for permissions / roles
    getPermissions: () => Promise.resolve(),
};
