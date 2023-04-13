import axios from 'axios';
import inMemoryJWT from './inMemoryJWT';
import history from '../utils/history';
import Cookies from 'js-cookie';


const apiclient = axios.create({
  baseURL: 'http://localhost:8005',
  withCredentials: true,
});

apiclient.interceptors.request.use(
  (config) => {
    let token = inMemoryJWT.getToken()
    let csrf_refresh_token = Cookies.get('csrf_refresh_token')
    if (token && config.url !== "/refresh") {
      config.headers["Authorization"] = `Bearer ${token}`;
    } else if (csrf_refresh_token && config.url === "/refresh") {
      config.headers["X-CSRF-TOKEN"] = csrf_refresh_token;
    }
    return config;
  },
  (error) => {
    Promise.reject(error);
  }
);

apiclient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    let status = error.response ? error.response.status : null
    let path = history.location.pathname
    if ((status === 422 | status === 401 && error.response.config.url==='/refresh' ) && path !== "/") {
      if (inMemoryJWT.eraseToken()) {
        history.push("/")
      }
    }
    return Promise.reject(error);
  }
);

export const postLogin = (username, password) => {
  return apiclient.post("/login", {
    username,
    password
  })
}

export const postRegister = (fullname, username, email, password) => {
  return apiclient.post("/register", {
    fullname,
    username,
    email,
    password
  })
}

export const getNewToken = () => {
  return apiclient.post("/refresh")
}

export const deleteLogout = () => {
  return apiclient.delete("/logout")
}

export const getConverstaionHistory = () => {
  return apiclient.get("/conversations")
}

export const postClassify = message => {
  return apiclient.post("/classify", { message })
}

export const postExtract = message => {
  return apiclient.post("/extract", { message })
}