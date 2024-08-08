import React, { useState } from 'react';
import logo from './assets/kwaai.png';
import './Register.css';
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

    const handleUser = async () => {
        try {
            await login({ email, isRegistering })
        } catch (e) {
            notify(e)
        }
    }

    const handleChange = (e: { target: { value: React.SetStateAction<string>; }; }) => {
        setEmail(e.target.value)
    }

    return (
        <div className="auth-container">
            <img src={logo} alt="Kwaai Logo" className="logo" />
            <h1>{isRegistering ? "Register" : "Login"}</h1>
            <input type="email" id="email" placeholder="Email" className="input-field" onChange={handleChange} />
            <button onClick={handleUser} className="auth-button">{isRegistering ? "Register" : "Login"}</button>
            <p className="auth-link">{isRegistering ? "Already have an account?" : "Don't have an account?"} <button onClick={handleClick}>{isRegistering ? "Login here" : "Register here"}</button></p>
        </div>
    );
};

export default Login;