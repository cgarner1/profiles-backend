from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional

class AuthHandler:
    def __init__(self):
        self.ACCESS_TOKEN_EXPIRE_MIN = 30
        self.TOKEN_ALGO = "HS256"
        self.SECRET_KEY = "" # TODO config parse

        self.security = HTTPBearer()
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated ="auto")

    def get_password_hash(self, pwd):
        return self.pwd_context.hash(pwd)
    
    def verify_pwd(self, plaintext_pwd, hashword):
        return self.pwd_context.verify(plaintext_pwd, hashword)

    def authenticate_user(username, password):
        # TODO check via DB, get pwd
        # check if hashed pwd matches
        pass

    def create_access_token(self, data, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MIN)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.TOKEN_ALGO)
        return encoded_jwt