"""
Модуль для установки инструментов пентестинга на сервере
"""
import logging
from app.core.ssh_client import SSHClient

logger = logging.getLogger(__name__)


# Определение инструментов и команд их установки
TOOLS = {
    "nmap": {
        "check": "which nmap",
        "install": "apt-get update && apt-get install -y nmap",
    },
    "nikto": {
        "check": "which nikto",
        "install": "apt-get update && apt-get install -y nikto",
    },
    "sqlmap": {
        "check": "which sqlmap",
        "install": "apt-get update && apt-get install -y sqlmap",
    },
    "nuclei": {
        "check": "which nuclei",
        "install": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest || (wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.2.7_linux_amd64.zip && unzip -q nuclei_3.2.7_linux_amd64.zip && mv nuclei /usr/local/bin/ && chmod +x /usr/local/bin/nuclei)",
    },
    "dirb": {
        "check": "which dirb",
        "install": "apt-get update && apt-get install -y dirb",
    },
    "gobuster": {
        "check": "which gobuster",
        "install": "apt-get update && apt-get install -y gobuster",
    },
    "wpscan": {
        "check": "which wpscan",
        "install": "apt-get update && apt-get install -y wpscan",
    },
    "whatweb": {
        "check": "which whatweb",
        "install": "apt-get update && apt-get install -y whatweb",
    },
    "subfinder": {
        "check": "which subfinder",
        "install": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || (wget -q https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_2.6.7_linux_amd64.zip && unzip -q subfinder_2.6.7_linux_amd64.zip && mv subfinder /usr/local/bin/ && chmod +x /usr/local/bin/subfinder)",
    },
    "httpx": {
        "check": "which httpx",
        "install": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest || (wget -q https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_1.3.7_linux_amd64.zip && unzip -q httpx_1.3.7_linux_amd64.zip && mv httpx /usr/local/bin/ && chmod +x /usr/local/bin/httpx)",
    },
}


def ensure_tools_installed(ssh_client: SSHClient) -> dict:
    """
    Проверка и установка всех необходимых инструментов
    Returns: dict с результатами установки {tool_name: installed}
    """
    results = {}
    
    for tool_name, tool_config in TOOLS.items():
        try:
            # Проверяем установлен ли инструмент
            if ssh_client.check_tool_installed(tool_name):
                logger.info(f"✅ {tool_name} уже установлен")
                results[tool_name] = True
            else:
                # Устанавливаем инструмент
                logger.info(f"📦 Установка {tool_name}...")
                installed = ssh_client.install_tool(tool_name, tool_config["install"])
                results[tool_name] = installed
        except Exception as e:
            logger.error(f"❌ Ошибка при работе с {tool_name}: {e}")
            results[tool_name] = False
    
    return results


def check_all_tools(ssh_client: SSHClient) -> dict:
    """Проверка наличия всех инструментов"""
    results = {}
    for tool_name in TOOLS.keys():
        results[tool_name] = ssh_client.check_tool_installed(tool_name)
    return results

