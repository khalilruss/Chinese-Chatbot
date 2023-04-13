import { createContext, useContext } from 'react';
import inMemoryJWT from '../utils/inMemoryJWT'
import { deleteLogout } from '../utils/api-client'
import { withRouter } from 'react-router-dom';
import jwt_decode from "jwt-decode";
import Cookies from 'js-cookie';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
}

const AuthProvider = ({ children, history }) => {

  const logout = () => {
    deleteLogout().then(() => {
      inMemoryJWT.eraseToken()
      history.push("/")
    }).catch(error => {
      console.error(error)
    })
  }

  const checkAuth = () => {
    if (inMemoryJWT.getToken() === null && Cookies.get('csrf_refresh_token')) {
      inMemoryJWT.getRefreshedToken()
    }
    return inMemoryJWT.waitForTokenRefresh().then(() => {
      if (inMemoryJWT.getToken() === null) {
        return Promise.reject()
      }
      let tokenExp = jwt_decode(inMemoryJWT.getToken()).exp
      let current_time = Date.now() / 1000;
      return current_time >= tokenExp ? Promise.reject() : Promise.resolve();
    });
  }

  return (
    <AuthContext.Provider value={{logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export default withRouter(AuthProvider);