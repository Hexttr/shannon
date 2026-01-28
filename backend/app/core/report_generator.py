"""
Генерация PDF отчетов
"""
import os
from sqlalchemy.orm import Session
from app.models.pentest import Pentest
from app.models.vulnerability import Vulnerability
from app.core.claude_client import ClaudeClient


def generate_pdf_report(pentest_id: int, db: Session):
    """Генерация PDF отчета из Markdown"""
    pentest = db.query(Pentest).filter(Pentest.id == pentest_id).first()
    if not pentest:
        raise ValueError("Пентест не найден")
    
    # Читаем Markdown отчет
    markdown_path = f"reports/pentest_{pentest_id}.md"
    if not os.path.exists(markdown_path):
        raise ValueError("Markdown отчет не найден")
    
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
    except FileNotFoundError:
        # Если Markdown файла нет, генерируем его
        from app.core.claude_client import ClaudeClient
        claude_client = ClaudeClient()
        vulnerabilities = db.query(Vulnerability).filter(Vulnerability.pentest_id == pentest_id).all()
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
        markdown_content = claude_client.generate_report(
            pentest.name,
            pentest.target_url,
            vulnerabilities_data,
            summary
        )
        # Сохраняем Markdown
        os.makedirs("reports", exist_ok=True)
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
    
    # Конвертируем Markdown в PDF используя WeasyPrint или другой инструмент
    # Для простоты используем markdown2pdf или reportlab
    try:
        import markdown
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Конвертируем Markdown в HTML
        try:
            html_content = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
        except:
            # Fallback без расширений
            html_content = markdown.markdown(markdown_content)
        
        # Стили для PDF
        css_content = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }
        h1 { color: #d32f2f; }
        h2 { color: #1976d2; margin-top: 1.5em; }
        code { background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
        """
        
        # Генерируем PDF
        pdf_path = f"reports/pentest_{pentest_id}.pdf"
        font_config = FontConfiguration()
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=css_content)],
            font_config=font_config
        )
        
        return pdf_path
        
    except ImportError:
        # Fallback: используем простой способ через markdown2pdf
        try:
            import markdown2
            from xhtml2pdf import pisa
            
            html_content = markdown2.markdown(markdown_content)
            pdf_path = f"reports/pentest_{pentest_id}.pdf"
            
            with open(pdf_path, "w+b") as pdf_file:
                pisa.CreatePDF(html_content, dest=pdf_file)
            
            return pdf_path
        except ImportError:
            # Если библиотеки не установлены, просто создаем текстовый файл
            pdf_path = f"reports/pentest_{pentest_id}.pdf"
            with open(pdf_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            return pdf_path

