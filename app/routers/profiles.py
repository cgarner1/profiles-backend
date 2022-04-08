import time
from fastapi import APIRouter, Request, Response, status #  ,Body, HTTPException, status
from .models import UserProfile
from bson.objectid import ObjectId

db_collection = "profiles"
router = APIRouter()

@router.post("/profiles", status_code=201)
async def create_profile(req: Request, response: Response, profile: UserProfile):
    timestamp = time.time()
    created_profile = profile.dict()
    created_profile['timestamp'] = str(timestamp)
    
    db_res = await req.app.db[db_collection].insert_one(created_profile)
    if(db_res.acknowledged):
        created_profile['_id'] = str(created_profile['_id'])
        return created_profile

    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"error" : "failed to write profile to db"}

@router.get("/profiles/{profile_id}", status_code=200)
async def get_profile(request: Request, response: Response, profile_id: str):
    # will throw internal error upon unformmated BSON objectID.
    # later update to UUID
    res = await request.app.db[db_collection].find_one({"_id": ObjectId(profile_id)})
    
    if not res:
        response.status_code = status.HTTP_204_NO_CONTENT
        return res
    
    res['_id'] = str(res['_id'])
    return res

@router.patch("/profiles/{profile_id}")
async def update_profiles(profile_id : int):
    
    return {"message": "Hello World"}

@router.delete("/profiles/{profile_id}", status_code=202)
async def delete_profile(request: Request, response: Response, profile_id : str):
    res = await request.app.db[db_collection].delete_one({"_id": ObjectId(profile_id)})
    
    # validation for resource acces done between API gateway and authz service
    if res.deleted_count == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    
    return { "id": profile_id }