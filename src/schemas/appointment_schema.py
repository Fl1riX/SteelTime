from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AppointmentCreate(BaseModel):
    date: datetime
    comment: str
    service_id: int
    entrepreneur_id: int
    user_id: int
    
    model_config = ConfigDict(extra='forbid')

class AppointmentResponse(AppointmentCreate):
    id: int
    
    class Config:
        from_attributes = True