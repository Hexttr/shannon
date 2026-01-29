import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.pentest import Pentest, PentestStatus
from app.models.vulnerability import Vulnerability
from app.core.claude_client import ClaudeClient
from app.core.report_generator import generate_pdf_report

router = APIRouter(prefix="/api/pentests", tags=["reports"])


@router.post("/{pentest_id}/reports")
def generate_report(
    pentest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Генерация отчета для пентеста"""
    pentest = db.query(Pentest).filter(Pentest.id == pentest_id).first()
    if not pentest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пентест не найден"
        )
    
    if pentest.status != PentestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отчет можно сгенерировать только для завершенного пентеста"
        )
    
    # Получаем уязвимости
    vulnerabilities = db.query(Vulnerability).filter(Vulnerability.pentest_id == pentest_id).all()
    
    # Генерируем отчет через Claude
    claude_client = ClaudeClient()
    vulnerabilities_data = [
        {
            "type": v.type,
            "title": v.title,
            "severity": v.severity.value,
            "description": v.description or "",
            "location": v.location or "",
            "cvss_score": v.cvss_score,
            "exploit": v.exploit or "",
            "recommendation": v.recommendation or ""
        }
        for v in vulnerabilities
    ]
    
    summary = f"Найдено {len(vulnerabilities)} уязвимостей"
    report_markdown = claude_client.generate_report(
        pentest.name,
        pentest.target_url,
        vulnerabilities_data,
        summary
    )
    
    # Сохраняем Markdown отчет
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    markdown_path = f"{reports_dir}/pentest_{pentest_id}.md"
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)
    
    return {"message": "Отчет сгенерирован", "markdown_path": markdown_path}


@router.get("/{pentest_id}/reports/check")
def check_report_exists(
    pentest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Проверка наличия отчета"""
    pentest = db.query(Pentest).filter(Pentest.id == pentest_id).first()
    if not pentest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пентест не найден"
        )
    
    pdf_path = f"reports/pentest_{pentest_id}.pdf"
    exists = os.path.exists(pdf_path)
    
    return {"exists": exists}


@router.get("/{pentest_id}/reports/pdf")
def download_pdf_report(
    pentest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Скачивание PDF отчета"""
    pentest = db.query(Pentest).filter(Pentest.id == pentest_id).first()
    if not pentest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пентест не найден"
        )
    
    pdf_path = f"reports/pentest_{pentest_id}.pdf"
    
    if not os.path.exists(pdf_path):
        # Генерируем PDF если его нет
        generate_pdf_report(pentest_id, db)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF отчет не найден"
        )
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"pentest-report-{pentest_id}.pdf"
    )


