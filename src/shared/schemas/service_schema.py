from pydantic import BaseModel, ConfigDict
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    price: int
    description: str
    duration: str
    address: str
    
    class Config:
        from_attributes = True
    
class ServiceCreate(ServiceBase):
    fullname: Optional[str] = None
    
    model_config = ConfigDict(extra='forbid')
    
class ServiceResponse(ServiceBase):
    id: int
    
    model_config = ConfigDict(extra='forbid')
    