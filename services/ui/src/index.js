import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { Router } from "react-router";
import history from "./utils/history";
import AuthProvider from "./context/Auth";

ReactDOM.render(
  <React.StrictMode>
    <Router history={history}>
      <AuthProvider >
        <App />
      </AuthProvider >
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
);
