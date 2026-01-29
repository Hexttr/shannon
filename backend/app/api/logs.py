from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.log import Log
from app.models.pentest import Pentest
from app.schemas.log import LogResponse

router = APIRouter(prefix="/api/pentests", tags=["logs"])


@router.get("/{pentest_id}/logs", response_model=List[LogResponse])
def get_logs(
    pentest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение логов пентеста"""
    pentest = db.query(Pentest).filter(Pentest.id == pentest_id).first()
    if not pentest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пентест не найден"
        )
    
    return db.query(Log).filter(Log.pentest_id == pentest_id).order_by(Log.timestamp).all()


