from fastapi import HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from db import get_user, fake_users_db, get_users
from models import TokenData, User
from security import SECRET_KEY, ALGORITHM, authenticate_user_with_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_all_of_users():
    return get_users(fake_users_db)


async def authenticate_token(token: str = Query(None)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized user"
    )
    if token:
        return authenticate_user_with_token(fake_users_db, token)
    else:
        raise credentials_exception
