from typing import Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    """profile schema expected in body"""
    name: str
    account_name: Optional[str] = None
    username: str
    # todo, on instantiation, add timestamp
