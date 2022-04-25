from datetime import timedelta
import time
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from .models import *
from bson.objectid import ObjectId
from .auth import *
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

db_collection = "profiles"
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/token", response_model=Token)
async def login_for_access_token(login_creds: UserLoginData, request: Request):
    user = await authenticate_user(login_creds.username, login_creds.password, request.app.db[db_collection])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": str(user["_id"])}) # TODO, passs in roles etc
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user_from_token(req: Request, token: str = Depends(oauth2_scheme)):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= TOKEN_ALGO)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(username=user_id)
    
    except JWTError:
        raise credentials_exception
    
    user = await req.app.db[db_collection].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise credentials_exception
    del user['password']
    user['_id'] = str(user['_id'])
    return user

@router.get("/profiles/me")
async def read_users_me(current_user = Depends(get_current_user_from_token)):   
    return current_user

@router.post("/profiles", status_code=201)
async def create_player_profile(req: Request, response: Response, profile: CreateProfileBody):
    timestamp = str(time.time())
    profile.password = get_password_hash(profile.password)
    created_profile = profile.dict()
    created_profile["created_at"] = timestamp
    created_profile["last_updated"] = timestamp
    created_profile["roles"] = ["player"]

    # TODO try router.app
    db_res = await req.app.db[db_collection].insert_one(created_profile)
    if not db_res.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add profile to Database"
        )
    created_profile['_id'] = str(created_profile['_id'])
    del created_profile['password']

    return created_profile


@router.get("/profiles/{profile_id}", status_code=200)
async def get_profile_any(request: Request, response: Response, profile_id: str):
    """Basic data for any profile, do not send any private info in this route"""
    # will throw internal error upon unformmated BSON objectID in query due to cast
    res = await request.app.db[db_collection].find_one({"_id": ObjectId(profile_id)})
    
    if not res:
        response.status_code = status.HTTP_204_NO_CONTENT
        return res
    
    res['_id'] = str(res['_id'])
    return res

@router.put("/profiles", status_code=200)
async def update_profile(request:Request, response: Response, profile: UserProfile, token: str = Depends(oauth2_scheme)):
    user_id = get_userid_from_token(token)
    
    if user_id != profile['_id']:
        raise credentials_exception
    
    res = await request.app.db[db_collection].update_one({"_id": profile["_id"]}, {"$set": profile.dict})
    if res.modified_count < 1:
        response.status_code = status.HTTP_404
        return {"msg": "failed to find resource id"}
    return profile.dict()

@router.delete("/profiles/{profile_id}", status_code=202)
async def delete_profile(request: Request, response: Response, profile_id : str, token: str = Depends(oauth2_scheme)):
    user_id = get_userid_from_token(token)
    
    if user_id != profile_id:
        raise credentials_exception
    
    res = await request.app.db[db_collection].delete_one({"_id": ObjectId(profile_id)})
    
    # validation for resource acces done between API gateway and authz service
    if res.deleted_count == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    
    return { "id": profile_id }