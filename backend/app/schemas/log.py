from pydantic import BaseModel
from datetime import datetime
from app.models.log import LogLevel


class LogResponse(BaseModel):
    id: int
    pentest_id: int
    level: LogLevel
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

