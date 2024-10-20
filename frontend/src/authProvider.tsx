import { AuthProvider, useNotify } from "react-admin";
import { authentication, logout } from "./apis/auth";
import { jwtDecode } from "jwt-decode";

interface CustomJwtPayload {
    roles: string[];
    exp?: number;
}

export const authProvider: AuthProvider = {
    // called when the user attempts to log in
    login: async (email: string) => {
        const notify = useNotify()
        try {
            const res = await authentication(email)
            if (res.token) {
                localStorage.setItem("token", res.token)
                return Promise.resolve()
            } else {
                notify('Verify your email address.', { type: 'success' });
            }
        } catch (e) {
            return Promise.reject(e)
        }
    },
    // called when the user clicks on the logout button
    logout: () => {
        logout()
        localStorage.removeItem("token")
        return Promise.resolve();
    },
    // called when the API returns an error
    checkError: ({ status }: { status: number }) => {
        if (status === 401 || status === 403) {
            logout()
            localStorage.removeItem("token")
            return Promise.reject();
        }
        return Promise.resolve();
    },
    // called when the user navigates to a new location, to check for authentication
    checkAuth: () => {
        const token = localStorage.getItem("token")
        if (!token) return Promise.reject()

        const decodeToken = jwtDecode(token!);
        const currentTime = Math.floor(Date.now() / 1000);

        if (decodeToken.exp && decodeToken.exp > currentTime) {
            return Promise.resolve()
        }
        return Promise.reject()
    },
    // called when the user navigates to a new location, to check for permissions / roles
    getPermissions: () => {
        const token = localStorage.getItem("token");
        if (!token) return Promise.reject();

        const decodedToken = jwtDecode<CustomJwtPayload>(token);
        return Promise.resolve(decodedToken.roles);
    },
};
