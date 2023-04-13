from datetime import timedelta, datetime

def create_token_response(account, Authorize):
    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=1)
    access_token = Authorize.create_access_token(subject=account.username, expires_time=access_token_expires)
    refresh_token = Authorize.create_refresh_token(subject=account.username, expires_time=refresh_token_expires)
    return access_token, refresh_token, refresh_token_expires

