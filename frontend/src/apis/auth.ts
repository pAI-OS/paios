import {
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser";

export const login = async (email: string) => {
  try {
    const response = await fetch(
      "/api/v1/auth/login/start",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      }
    );

    if (response.status !== 200) {
      throw new Error("Failed to generate Login options");
    }

    const res = await response.json();
    const options = JSON.parse(res?.options);
    const authResp = await startAuthentication(options);

    const verifyResponse = await fetch(
      "/api/v1/auth/login/finish",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          auth_resp: authResp,
          challenge: options.challenge,
        }),
      }
    );

    if (verifyResponse.status !== 200) {
      throw new Error("Failed to register user.");
    }
    return true
  } catch (error) {
    throw new Error("Failed to register user");
  }
};

export const register = async (email: string) => {
  try {
    const response = await fetch(
      "/api/v1/auth/register/start",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      }
    );

    if (response.status === 409) {
      throw new Error("User already exists");
    }

    if (response.status !== 200) {
      throw new Error("Failed to generate registration options");
    }

    const res = await response.json();
    const options = JSON.parse(res?.options);

    const attResp = await startRegistration(options);

    const verifyResponse = await fetch(
      "/api/v1/auth/register/finish",
      {
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
      }
    );

    if (verifyResponse.status !== 200) {
      throw new Error("Failed to register user.");
    }
    return true
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to register user");
  }
};

export const logout = async () => {
  await fetch("/api/v1/auth/logout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
};
