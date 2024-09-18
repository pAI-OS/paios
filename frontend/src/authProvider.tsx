import { AuthProvider } from "react-admin";
import { login, register, logout } from "./apis/auth";
import { jwtDecode } from "jwt-decode";

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
                localStorage.setItem("token", response.token)
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
    getPermissions: () => Promise.resolve(),
};
