import './Register.css'
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Image, Card } from "react-bootstrap/";
import Form from 'react-bootstrap/Form'
import logoImg from "../../assets/chatbotlogo.svg";
import validator from 'validator'
import { postRegister } from '../../utils/api-client'
import jwt_decode from "jwt-decode";
import inMemoryJWT from '../../utils/inMemoryJWT'

const Register = ({ history }) => {
    const [errorText, setErrorText] = useState("")
    const [fullname, setFullname] = useState("");
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const register = (fullname, username, email, password) => {
        postRegister(fullname, username, email, password)
            .then(result => {
                if (result.status === 201) {
                    let dataObj = JSON.parse(JSON.stringify(result.data))
                    inMemoryJWT.setToken(dataObj.access_token, jwt_decode(dataObj.access_token).exp);
                    history.push("/home");
                }
            }).catch(e => {
                if (e.response) {
                    setErrorText(e.response.data.detail)
                } else {
                    setErrorText("An error has occured while trying to register your account \n please try again later")
                }
            });
    }

    const submitRegister = () => {
        if (
            fullname != "" &&
            email != "" &&
            username != "" &&
            password != "" &&
            confirmPassword != ""
        ) {
            if (validator.isEmail(email)) {
                if (password.length >= 8) {
                    if (password === confirmPassword) {
                        register(fullname, username, email, password)
                    } else {
                        setErrorText('The passwords you entered do not match');
                    }
                } else {
                    setErrorText('Your password must be at least 8 characters long');
                }
            } else {
                setErrorText('Please enter a valid email');
            }
        } else {
            setErrorText('Please complete all of the fields')
        }


    }

    const handleKeypress = e => {
        if (e.charCode === 13) {
            submitRegister();
        }
    };

    return (
        <div className="register-wrapper">
            <Card className='card'>
                <Image src={logoImg} className='register-logo' />
                <h2>清注册账户</h2>
                <h2 className='register-english'>(Please register an account)</h2>
                <Form className='form'>
                    <Form.Control
                        className='input'
                        type="fullname"
                        value={fullname}
                        onChange={e => {
                            setFullname(e.target.value);
                        }}
                        placeholder="Fullname"
                    />
                    <Form.Control
                        className='input'
                        type="username"
                        value={username}
                        onChange={e => {
                            setUsername(e.target.value);
                        }}
                        placeholder="Username"
                    />
                    <Form.Control
                        className='input'
                        type="email"
                        value={email}
                        onChange={e => {
                            setEmail(e.target.value);
                        }}
                        placeholder="Email"
                    />
                    <Form.Control
                        className='input'
                        type="password"
                        value={password}
                        onChange={e => {
                            setPassword(e.target.value);
                        }}
                        placeholder="Password"
                    />
                    <Form.Control
                        className='input'
                        type="password"
                        value={confirmPassword}
                        onChange={e => {
                            setConfirmPassword(e.target.value);
                        }}
                        onKeyPress={e => handleKeypress(e)}
                        placeholder="Confirm Password"
                    />
                    <Button
                        className='button'
                        onClick={() => submitRegister()}>注册 (Register)
                    </Button>
                </Form>
                <Link to="/">已经有账户吗？ (Already have an account?)</Link>
                {errorText != "" && <div className='error'>{errorText}</div>}
            </Card>
        </div>
    )
}

export default Register