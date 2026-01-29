"""
Клиент для работы с Claude API (Anthropic)
"""
import anthropic
from typing import List, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Клиент для Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4.5
    
    def analyze_scan_results(
        self,
        tool_name: str,
        target_url: str,
        scan_output: str
    ) -> Dict[str, Any]:
        """
        Анализ результатов сканирования инструментом
        
        Returns: {
            "vulnerabilities": [...],
            "summary": "...",
            "recommendations": "..."
        }
        """
        prompt = f"""Ты эксперт по кибербезопасности. Проанализируй результаты сканирования безопасности.

Инструмент: {tool_name}
Цель: {target_url}

Результаты сканирования:
{scan_output}

Задачи:
1. Определи все найденные уязвимости
2. Классифицируй каждую уязвимость по уровню критичности (critical/high/medium/low)
3. Оцени CVSS score для каждой уязвимости (0.0-10.0)
4. Сгенерируй эксплойт для каждой уязвимости (если возможно)
5. Предоставь рекомендации по исправлению

Верни результат в формате JSON:
{{
    "vulnerabilities": [
        {{
            "type": "тип уязвимости (SQL Injection, XSS, etc.)",
            "title": "краткое название",
            "severity": "critical|high|medium|low",
            "description": "подробное описание",
            "location": "URL или путь где найдена",
            "cvss_score": 9.5,
            "exploit": "пример эксплойта или команды",
            "recommendation": "рекомендация по исправлению"
        }}
    ],
    "summary": "краткое резюме сканирования",
    "recommendations": "общие рекомендации"
}}

Если уязвимостей не найдено, верни пустой массив vulnerabilities."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Извлекаем текст ответа
            response_text = message.content[0].text
            
            # Парсим JSON из ответа
            import json
            # Ищем JSON в ответе (может быть обернут в markdown код блоки)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при анализе результатов Claude: {e}")
            # Возвращаем пустой результат при ошибке
            return {
                "vulnerabilities": [],
                "summary": f"Ошибка анализа: {str(e)}",
                "recommendations": ""
            }
    
    def generate_report(
        self,
        pentest_name: str,
        target_url: str,
        vulnerabilities: List[Dict[str, Any]],
        summary: str
    ) -> str:
        """
        Генерация отчета в формате Markdown
        """
        vulnerabilities_text = "\n\n".join([
            f"### {i+1}. {v['title']}\n\n"
            f"**Тип:** {v['type']}\n"
            f"**Критичность:** {v['severity']}\n"
            f"**CVSS Score:** {v.get('cvss_score', 'N/A')}\n"
            f"**Местоположение:** {v.get('location', 'N/A')}\n\n"
            f"**Описание:**\n{v['description']}\n\n"
            f"**Эксплойт:**\n```\n{v.get('exploit', 'N/A')}\n```\n\n"
            f"**Рекомендация:**\n{v.get('recommendation', 'N/A')}\n"
            for i, v in enumerate(vulnerabilities)
        ])
        
        prompt = f"""Создай профессиональный отчет о пентесте в формате Markdown.

Название пентеста: {pentest_name}
Цель: {target_url}

Найденные уязвимости:
{vulnerabilities_text}

Краткое резюме: {summary}

Создай отчет со следующей структурой:
1. Титульная страница с названием и датой
2. Executive Summary
3. Методология
4. Найденные уязвимости (детальное описание каждой)
5. Рекомендации по исправлению
6. Заключение

Используй профессиональный стиль, подходящий для технического отчета."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Ошибка при генерации отчета: {e}")
            return f"# Отчет о пентесте\n\nОшибка генерации отчета: {str(e)}"


