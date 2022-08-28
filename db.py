from models import UserInDB, User

fake_users_db = {
    "shahin1": {
        "username": "shahin1",
        "full_name": "shahin Abolghasemi",
        "email": "mail@example.com",
        "hashed_password": "$2b$12$que3HWIumJszuE3sytBUrOMWa.kNaHZLkrt2oWqTT28OAK4X8AJIm",
        "disabled": False,
    },
    "shahin2": {
        "username": "shahin2",
        "full_name": "shahin Abolghasemi",
        "email": "mail@example.com",
        "hashed_password": "$2b$12$que3HWIumJszuE3sytBUrOMWa.kNaHZLkrt2oWqTT28OAK4X8AJIm",
        "disabled": False,
    },
}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def get_user_info(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)


def get_users(db):
    return [User(**db[user]) for user in db]
