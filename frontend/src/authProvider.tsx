import { AuthProvider } from "react-admin";
import { login, register, logout } from "./apis/auth";

export const authProvider: AuthProvider = {
    // called when the user attempts to log in
    login: async ({ email, isRegistering }) => {
        let response
        try {
            if (isRegistering) {
                response = await register(email)
            } else {
                response = await login(email)
            }
            if (response) {
                localStorage.setItem("authenticated", "true")
            } else {
                return Promise.reject()
            }
            return Promise.resolve()
        } catch (e) {
            return Promise.reject(e)
        }
    },
    // called when the user clicks on the logout button
    logout: () => {
        logout()
        localStorage.removeItem("authenticated")
        return Promise.resolve();
    },
    // called when the API returns an error
    checkError: ({ status }: { status: number }) => {
        if (status === 401 || status === 403) {
            logout()
            localStorage.removeItem("authenticated")
            return Promise.reject();
        }
        return Promise.resolve();
    },
    // called when the user navigates to a new location, to check for authentication
    checkAuth: () => {
        return localStorage.getItem("authenticated")
            ? Promise.resolve()
            : Promise.reject();
    },
    // called when the user navigates to a new location, to check for permissions / roles
    getPermissions: () => Promise.resolve(),
};
