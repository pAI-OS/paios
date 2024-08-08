import {
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser";

export const login = async (email: string) => {
  try {
    const response = await fetch(
      "http://localhost:3080/api/v1/webauthn/generate-authentication-options",
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
      "http://localhost:3080/api/v1/webauthn/verify-authentication",
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
  } catch (error) {
    throw new Error("Failed to register user");
  }
};

export const register = async (email: string) => {
  try {
    const response = await fetch(
      "http://localhost:3080/api/v1/webauthn/generate-registration-options",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      }
    );

    if (response.status !== 200) {
      throw new Error("Failed to generate registration options");
    }

    const res = await response.json();
    const options = JSON.parse(res?.options);

    const attResp = await startRegistration(options);

    const verifyResponse = await fetch(
      "http://localhost:3080/api/v1/webauthn/verify-registration",
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
      throw new Error("Failed to Login user.");
    }
  } catch (error) {
    throw new Error("Failed to login user");
  }
};
