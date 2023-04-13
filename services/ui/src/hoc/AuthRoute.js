import React, { useState, useEffect } from "react";
import { Route, Redirect } from "react-router-dom";
import { useAuth } from "../context/Auth";
import "bootstrap/dist/css/bootstrap.min.css";
import Spinner from 'react-bootstrap-spinner';

const AuthRoute = ({ component: Component, ...rest }) => {
  const { checkAuth } = useAuth();
  const [authState, setAuthState] = useState('loading');
  const requireAuthRoutes = ['ConversationHistory', 'Home', 'Chat']
  const noAuthRoutes = ['Login', 'Register']
  
  useEffect(() => {
    checkAuth().then(() => {
      setAuthState('loggedin')
    }).catch(() => {
      setAuthState('redirect')
    });
  });

  if (authState === 'loading') {
    return (
      <div className='home'>
        <Spinner type="border" color="primary" size="20" />
      </div>
    )
  }
  return (
    <Route
      {...rest}
      render={props => {
        if (authState === 'loggedin') {
          if (requireAuthRoutes.includes(Component.name)) {
            return <Component {...props} />
          } else {
            return <Redirect to="/home" />
          }

        } else {
          if (noAuthRoutes.includes(Component.name)) {
            return <Component {...props} />
          } else {
            return <Redirect to="/" />
          }
        }
      }

      }
    />
  );
}

export default AuthRoute;