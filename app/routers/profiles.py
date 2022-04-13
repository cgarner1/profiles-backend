import time
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from .models import UserProfile, AuthnUserProfile, TokenData, Token
from bson.objectid import ObjectId
from .auth import AuthHandler
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

db_collection = "profiles"
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(req: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, AuthHandler.SECRET_KEY, algorithms=AuthHandler.TOKEN_ALGO)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(username=user_id)
    
    except JWTError:
        raise credentials_exception
    user = await req.app.db[db_collection].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise credentials_exception
    return user


# @app.post("/token", response_model=Token)
# async def access_token_login()

@router.post("/profiles", status_code=201)
async def create_profile(req: Request, response: Response, profile: AuthnUserProfile):
    timestamp = str(time.time())
    created_profile = profile.dict()
    created_profile["created_at"] = timestamp
    created_profile["last_updated"] = timestamp

    # generate a baseId

    
    db_res = await req.app.db[db_collection].insert_one(created_profile)
    if(db_res.acknowledged):
        created_profile['_id'] = str(created_profile['_id'])

        # generate + send JWT
        return created_profile

    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"error" : "failed to write profile to db"}

@router.get("/profiles/{profile_id}", status_code=200)
async def get_profile(request: Request, response: Response, profile_id: str):
    """Basic data for any profile, do not send any private info in this route"""
    # will throw internal error upon unformmated BSON objectID in query due to cast
    # later update to UUID
    res = await request.app.db[db_collection].find_one({"_id": ObjectId(profile_id)})
    
    if not res:
        response.status_code = status.HTTP_204_NO_CONTENT
        return res
    
    res['_id'] = str(res['_id'])
    return res

@router.put("/profiles", status_code=200)
async def update_profiles(request:Request, response: Response, profile: UserProfile):
    # todo add authz for this
    res = await request.app.db[db_collection].update_one({"_id": profile["_id"]}, {"$set": profile.dict})
    if res.modified_count < 1:
        response.status_code = status.HTTP_404
        return {"msg": "failed to find resource id"}
    return profile.dict()

@router.delete("/profiles/{profile_id}", status_code=202)
async def delete_profile(request: Request, response: Response, profile_id : str):
    # add authz for this
    res = await request.app.db[db_collection].delete_one({"_id": ObjectId(profile_id)})
    
    # validation for resource acces done between API gateway and authz service
    if res.deleted_count == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    
    return { "id": profile_id }