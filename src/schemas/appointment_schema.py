from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class AppointmentCreate(BaseModel):
    date: datetime
    comment: str = Field(max_length=1200)
    service_id: int
    entrepreneur_id: int
    
    model_config = ConfigDict(extra='forbid')

class AppointmentResponse(AppointmentCreate):
    id: int
    
    class Config:
        from_attributes = True