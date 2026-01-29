from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.models.pentest import Pentest
from app.schemas.vulnerability import VulnerabilityResponse

router = APIRouter(prefix="/api/pentests", tags=["vulnerabilities"])


@router.get("/{pentest_id}/vulnerabilities", response_model=List[VulnerabilityResponse])
def get_vulnerabilities(
    pentest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка уязвимостей для пентеста"""
    pentest = db.query(Pentest).filter(Pentest.id == pentest_id).first()
    if not pentest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пентест не найден"
        )
    
    return db.query(Vulnerability).filter(Vulnerability.pentest_id == pentest_id).all()


