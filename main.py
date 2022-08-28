import copy
from datetime import timedelta
from typing import Union, List

from fastapi import FastAPI, WebSocket, Query, Cookie, status, Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

from db import fake_users_db
from dependencies import get_current_active_user, get_all_of_users, authenticate_token
from models import Token, User
from security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

INIT_ALIVE_USER = {
    "messages": [],
    "websocket": None,
}

app = FastAPI()

templates = Jinja2Templates(directory='templates')

alive_users = dict()


async def get_cookie_or_token(
        websocket: WebSocket,
        session: Union[str, None] = Cookie(default=None),
        token: Union[str, None] = Query(default=None),
):
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.get('/')
def root(request: Request):
    with open('./templates/index.html', 'r') as f:
        return templates.TemplateResponse("index.html", {'request': request})


@app.get('/chats')
def messages():
    return alive_users


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(authenticate_token)):
    await websocket.accept()
    alive_user = alive_users.get(user.username)
    if alive_user is None:
        alive_users[user.username] = copy.deepcopy(INIT_ALIVE_USER)
        alive_users[user.username]['websocket'] = websocket
    elif alive_user.get('websocket') is None:
        alive_user['websocket'] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            print(f"from: {user.username} message: {data.get('message')}")
            send_to = data.get('to')

            target_user = alive_users.get(send_to)
            if target_user:
                if send_to == user.username:
                    await target_user['websocket'].send_text(f"hey {user.username}, how u doing? r u ok ? :/")
                else:
                    await target_user['websocket'].send_text(f"{user.username}: {data.get('message')}")
                # await websocket.send_text(f"message sent")
            else:
                await websocket.send_text(f"{send_to} is not alive or is not found in users")

    except WebSocketDisconnect as e:
        alive_users.pop(user.username)
        print(f'{user.username} disconnected')


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/user", response_model=List[User])
async def get_users(
        current_user: User = Depends(get_current_active_user),
        users: List[User] = Depends(get_all_of_users)
):
    return users


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, debug=True)
