import { getNewToken } from './api-client'
import jwt_decode from "jwt-decode";

const inMemoryJWTManager = () => {
    let inMemoryJWT = null;
    let isRefreshing = null;
    let logoutEventName = 'chatbot-logout';
    let refreshTimeOutId;

    const setLogoutEventName = name => logoutEventName = name;

    // This countdown feature is used to renew the JWT before it's no longer valid
    // in a way that is transparent to the user.
    const refreshToken = (delay) => {
        refreshTimeOutId = window.setTimeout(
            getRefreshedToken,
            delay * 1000 - 5000
        ); // Validity period of the token in seconds, minus 5 seconds
    };

    const abortRefreshToken = () => {
        if (refreshTimeOutId) {
            window.clearTimeout(refreshTimeOutId);
        }
    };

    const waitForTokenRefresh = () => {
        if (!isRefreshing) {
            return Promise.resolve();
        }
        return isRefreshing.then(() => {
            isRefreshing = null;
            return true;
        });
    }

    // The method make a call to the refresh-token endpoint
    // If there is a valid cookie, the endpoint will set a fresh jwt in memory.
    const getRefreshedToken = () => {
        isRefreshing = getNewToken()
            .then((response) => {
                if (response.status !== 200) {
                    eraseToken();
                    global.console.log(
                        'Token renewal failure'
                    );
                    return { token: null };
                }
                return JSON.parse(JSON.stringify(response.data));
            })
            .then((dataObj) => {
                if (dataObj.access_token != null) {
                    setToken(dataObj.access_token, jwt_decode(dataObj.access_token).exp);
                    return true;
                }
                eraseToken();
                return false;
            }).catch(e => {
                console.error(e)
            });

        return isRefreshing;
    };

    const getToken = () => inMemoryJWT;

    const setToken = (token, delay) => {
        inMemoryJWT = token;
        let current_time = Date.now() / 1000;
        let duration = Math.round(delay - current_time)
        refreshToken(duration);
        return true;
    };

    const eraseToken = () => {
        inMemoryJWT = null;
        abortRefreshToken();
        window.localStorage.setItem(logoutEventName, Date.now());
        return true;
    };

    // This listener will allow to disconnect a session of ra started in another tab
    window.addEventListener('storage', (event) => {
        if (event.key === logoutEventName) {
            inMemoryJWT = null;
        }
    });

    return {
        eraseToken,
        getRefreshedToken,
        getToken,
        setLogoutEventName,
        setToken,
        waitForTokenRefresh,
    }
};

export default inMemoryJWTManager();