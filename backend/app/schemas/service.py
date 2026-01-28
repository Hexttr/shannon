from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    url: str


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

