from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
from fastapi import status
from configparser import ConfigParser
import sys

config = ConfigParser()
config.read(f"{sys.path[0]}/routers/config.ini")

ACCESS_TOKEN_EXPIRE_MIN = 30
TOKEN_ALGO = "HS256"
SECRET_KEY = config['Auth']['jwt_secret']

security = HTTPBearer()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated ="auto")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)

def get_password_hash(pwd):
    return pwd_context.hash(pwd)
    
def verify_pwd(plaintext_pwd, hashword):
    return pwd_context.verify(plaintext_pwd, hashword)

async def authenticate_user(username, entered_password, database):
    # searching users w/o indexing... likely more expensive than necc
    
    user = await database.find_one({"username": username}) # TODO abstraction for database calls!
    if not user or not verify_pwd(entered_password, user["password"]):
        return {}
    return user

def create_access_token(data, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=TOKEN_ALGO)
    return encoded_jwt

def get_userid_from_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= TOKEN_ALGO)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    return user_id
    