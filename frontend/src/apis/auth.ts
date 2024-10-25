import {
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser";
import { apiBase } from "../apiBackend";

export const authentication = async (email: string) => {
  try {
    const response = await fetch(`${apiBase}/auth/webauthn/options`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    if (response.status !== 200) {
      throw new Error("Something went wrong");
    }

    const res = await response.json();
    const options = JSON.parse(res.options);
    if (res.flow === "REGISTER") return await register(email, options);
    else if (res.flow === "LOGIN") return await login(email, options);
  } catch (error) {
    throw new Error("Failed to register user");
  }
};

export const verifyEmail = async (token: string) => {
  try {
    const isValidRes = await fetch(`${apiBase}/auth/verify-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        token,
      }),
    });

    if (isValidRes.status !== 200) {
      throw new Error("Email validation failed.");
    }

    return await isValidRes.json();
  } catch (error) {
    throw new Error("Email validation failed.");
  }
};

export const login = async (email: string, options: any) => {
  try {
    const authResp = await startAuthentication(options);

    const verifyResponse = await fetch(`${apiBase}/auth/webauthn/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        auth_resp: authResp,
        challenge: options.challenge,
      }),
    });

    if (verifyResponse.status !== 200) {
      throw new Error("Failed to register user.");
    }

    return await verifyResponse.json();
  } catch (error) {
    throw new Error("Failed to register user");
  }
};

export const register = async (email: string, options: any) => {
  try {
    const attResp = await startRegistration(options);

    const verifyResponse = await fetch(`${apiBase}/auth/webauthn/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        att_resp: attResp,
        challenge: options.challenge,
        user_id: options.user.id,
      }),
    });

    if (verifyResponse.status !== 200) {
      throw new Error("Failed to register user.");
    }
    const tokenRes = await verifyResponse.json();
    return tokenRes;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to register user");
  }
};

export const logout = async () => {
  await fetch(`${apiBase}/auth/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
};
