from pydantic import BaseModel, ConfigDict

class ServiceCreate(BaseModel):
    name: str
    price: int
    description: str
    duration: str
    address: str
    
    model_config = ConfigDict(extra='forbid')

class ServiceResponse(ServiceCreate):
    id: int
    
    class Config:
        from_attributes = True