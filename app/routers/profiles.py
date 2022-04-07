import time
from fastapi import APIRouter, Request #  ,Body, HTTPException, status
from .models import UserProfile

router = APIRouter()

@router.post("/profiles")
async def create_profile(request: Request, profile: UserProfile):
    timestamp = time.time()
    created_profile = profile.dict()
    created_profile['timestamp'] = str(timestamp)
    res = await request.app.db["profiles"].insert_one(created_profile)

    # todo -> validate insert success
    return profile

@router.get("/profiles/{profile_id}")
async def get_profile(profile_id : int):

    return {"message": "Hello World"}

@router.patch("/profiles/{profile_id}")
async def update_profiles(profile_id : int):
    return {"message": "Hello World"}

@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id : int):
    return {'message': "Hello World"}

@router.post("/profiles/testdata")
async def populate_profiles_testdata():
    return {'status':'done'}
