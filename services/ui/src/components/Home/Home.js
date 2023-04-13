import './Home.css'
import React from "react";
import { useAuth } from "../../context/Auth";
import { Button, Image } from 'react-bootstrap';
import logoImg from "../../assets/chatbotlogo.svg";

const Home = ({ history }) => {
  const { logout } = useAuth();
  return (
    <div>
      <Image src={logoImg} className='home-logo' />
      <div className='home'>
        <div className='button-container'>
          <Button className='home-button' onClick={() => { history.push("/chat") }}>Chat to the Bot</Button>
          <Button className='home-button' onClick={() => { history.push("/conversations") }}>View Conversation History</Button>
          <Button className='home-button' onClick={() => { logout() }}>Logout</Button>
        </div>
      </div>
    </div>
  );
}

export default Home;