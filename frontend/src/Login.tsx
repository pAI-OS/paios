import React, { useState } from 'react';
import logo from './assets/kwaai.png';
import './Login.css';
import { useLogin, useNotify } from "react-admin"

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [isRegistering, setIsRegistering] = useState(true);

    const login = useLogin()
    const notify = useNotify()

    const handleClick = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
        event.preventDefault()
        setIsRegistering((prev) => !prev)
        setEmail("")
    }

    const handleUser = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        if (!email.trim()) {
            notify('Email field cannot be empty', { type: 'error' });
            return;
        }

        try {
            await login({ email, isRegistering });
        } catch (e) {
            console.error('Debug: Error in handleUser:', e);
            if (e instanceof Error) {
                if (e.name === 'InvalidStateError' || e.message.includes('The authenticator was previously registered')) {
                    notify('User already exists. Please login instead.', { type: 'error' });
                } else {
                    notify('An error occurred. Please try again.', { type: 'error' });
                }
            } else {
                notify('An unexpected error occurred. Please try again.', { type: 'error' });
            }
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setEmail(e.target.value)
    }

    return (
        <div className="auth-container">
            <h1 className="paios-heading">pAI-OS</h1>
            <img src={logo} alt="Kwaai Logo" className="logo" />
            <h2>{isRegistering ? "Register" : "Login"}</h2>
            <form onSubmit={handleUser}>
                <input type="email" id="email" placeholder="Email" className="input-field" onChange={handleChange} value={email} />
                <button type="submit" className="auth-button">{isRegistering ? "Register" : "Login"}</button>
            </form>
            <p className="auth-link">{isRegistering ? "Already have an account?" : "Don't have an account?"} <button onClick={handleClick}>{isRegistering ? "Login here" : "Register here"}</button></p>
        </div>
    );
};

export default Login;