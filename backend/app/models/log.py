from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    pentest_id = Column(Integer, ForeignKey("pentests.id"), nullable=False)
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pentest = relationship("Pentest", back_populates="logs")

