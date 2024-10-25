import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { verifyEmail } from './apis/auth';
import './Login.css';

export const VerifyEmail = () => {
    const { token } = useParams();
    const [verificationStatus, setVerificationStatus] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const checkEmail = async () => {
            if (!token) {
                setVerificationStatus("Not a valid token")
                return
            }
            setLoading(true)
            try {
                const res = await verifyEmail(token!);
                setVerificationStatus(res.message);
            } catch (error) {
                setVerificationStatus(error.message);
            } finally {
                setLoading(false);
            }
        };
        checkEmail();
    }, [token]);

    return (
        <div>
            <div className="verification-container">
                {loading ? (
                    <div className="loading">Loading...</div>
                ) : (
                    <div className="verification-message">
                        <h1>Email Verification Status</h1>
                        <p>{verificationStatus}</p>
                        <button className="login-button" onClick={() => navigate("/login")}>
                            Go to Login
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}