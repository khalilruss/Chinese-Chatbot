import './App.css';
import React from "react"
import Login from './components/Login/Login'
import Register from './components/Register/Register'
import Home from './components/Home/Home'
import Chat from './components/Chat/Chat'
import Conversations from './components/ConversationHistory/ConversationHistory'
import { Switch, Link, useLocation } from "react-router-dom";
import AuthRoute from './hoc/AuthRoute';
import Navbar from 'react-bootstrap/Navbar'
import { Nav } from 'react-bootstrap';
import logoImg from "./assets/chatbotlogo.svg";
import { useAuth } from "./context/Auth"


const App = () => {
  const { logout } = useAuth();
  let location = useLocation();

  const navbar = () => {
    return (<Navbar collapseOnSelect expand="lg" bg="light" variant="light" className='py-0'>
      <Navbar.Brand as={Link} to="/home">
        <img
          src={logoImg}
          width="110"
          height="50"
          alt="Chinese Chatbot logo"
        />
      </Navbar.Brand>
      <Navbar.Toggle aria-controls="responsive-navbar-nav" />
      <Navbar.Collapse id="responsive-navbar-nav">
        <Nav className="ml-auto">
          <Nav.Link as={Link} to="/chat" className='link-color'>Chat</Nav.Link>
          <Nav.Link as={Link} to="/conversations" className='link-color'>Conversation History</Nav.Link>
          <Nav.Link onClick={() => { logout() }} className='link-color'>Logout</Nav.Link>
        </Nav>
      </Navbar.Collapse>
    </Navbar>)
  }

  return (
    <div className="bg">
      {location.pathname != '/' && location.pathname != '/register' ? navbar() : null}
      <Switch>
        <AuthRoute exact path="/" component={Login} />
        <AuthRoute exact path="/register" component={Register} />
        <AuthRoute exact path="/home" component={Home} />
        <AuthRoute exact path="/chat" component={Chat} />
        <AuthRoute exact path="/conversations" component={Conversations} />
      </Switch>
    </div>
  );
}

export default App;
