import './Login.css'
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Image, Card } from "react-bootstrap/";
import Form from 'react-bootstrap/Form'
import logoImg from "../../assets/chatbotlogo.svg";
import { postLogin } from '../../utils/api-client'
import jwt_decode from "jwt-decode";
import inMemoryJWT from '../../utils/inMemoryJWT'

const Login = ({ history }) => {
  const [errorText, setErrorText] = useState("")
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  
  const login = (username, password, setErrorText) => {
    postLogin(username, password)
      .then(result => {
        if (result.status === 200) {
          let dataObj = JSON.parse(JSON.stringify(result.data))
          inMemoryJWT.setToken(dataObj.access_token, jwt_decode(dataObj.access_token).exp);
          history.push("/home")
        }
      }).catch(e => {
        if (e.response) {
          setErrorText(e.response.data.detail)
        }else {
          setErrorText("An error has occured while trying to login \n please try again later")
        }
      });
  }

  const submitLogin = () => {
    if (username != "" && password != "") {
      login(username, password, setErrorText)
    } else {
      setErrorText('Please complete all of the fields')
    }
  }

  const handleKeypress = e => {
    if (e.charCode === 13) {
      submitLogin();
    }
  };

  return (
    <Card className='card'>
      <Image src={logoImg} className='login-logo' />
      <h2>请登录</h2>
      <h2>(Please login)</h2>
      <Form className='form'>
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
          type="password"
          value={password}
          onChange={e => {
            setPassword(e.target.value);
          }}
          onKeyPress={e=>handleKeypress(e)}
          placeholder="Password"
        />
        <Button
          className='button'
          onClick={() => submitLogin()}>登录 (Sign In)
        </Button>
      </Form>
      <Link to="/register">没有账户吗？ (Don't have an account?)</Link>
      { errorText != "" && <div className='error'>{errorText}</div>}
    </Card>
  )
}

export default Login