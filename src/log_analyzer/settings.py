"""
Configuração centralizada para o projeto Log Analyzer
"""

import os
from pathlib import Path
from typing import Dict, Any

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Configurações da API
API_CONFIG = {
    "title": "Log Analyzer API",
    "description": "API REST para análise de logs de segurança cibernética",
    "version": "1.0.0",
    "host": os.getenv("API_HOST", "127.0.0.1"),
    "port": int(os.getenv("API_PORT", "8000")),
    "debug": os.getenv("API_DEBUG", "false").lower() == "true",
    "reload": os.getenv("API_RELOAD", "false").lower() == "true",
}

# Configurações de arquivo
FILE_CONFIG = {
    "max_size_mb": 100,
    "supported_extensions": [".csv", ".json"],
    "encoding_attempts": ["utf-8", "utf-8-sig", "latin1", "cp1252"],
}

# Configurações de análise
ANALYSIS_CONFIG = {
    "brute_force_threshold": 5,
    "high_risk_threshold": 10,
    "medium_risk_threshold": 5,
    "max_geographic_ips": 10,
    "max_suspicious_ips": 10,
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "app.log" if LOGS_DIR.exists() else None,
}

# Mensagens de erro padrão
ERROR_MESSAGES = {
    "NO_FILES": "Pelo menos um arquivo de log deve ser enviado",
    "INVALID_FORMAT": "Formato de arquivo não suportado",
    "FILE_TOO_LARGE": "Arquivo muito grande",
    "PROCESSING_ERROR": "Erro ao processar arquivo",
    "INTERNAL_ERROR": "Erro interno do servidor",
    "ANALYZER_UNAVAILABLE": "LogAnalyzer não disponível",
    "FASTAPI_UNAVAILABLE": "FastAPI não disponível",
}

# Configurações de segurança
SECURITY_CONFIG = {
    "allowed_origins": ["*"],  # Em produção, especificar origins
    "allow_credentials": True,
    "max_request_size": FILE_CONFIG["max_size_mb"] * 1024 * 1024,
}

# Configuração completa
CONFIG = {
    "api": API_CONFIG,
    "files": FILE_CONFIG,
    "analysis": ANALYSIS_CONFIG,
    "logging": LOGGING_CONFIG,
    "security": SECURITY_CONFIG,
    "errors": ERROR_MESSAGES,
}


def get_config() -> Dict[str, Any]:
    """Retorna configuração completa do projeto."""
    return CONFIG


def get_api_config() -> Dict[str, Any]:
    """Retorna configuração específica da API."""
    return API_CONFIG


def get_file_config() -> Dict[str, Any]:
    """Retorna configuração de arquivos."""
    return FILE_CONFIG


def get_analysis_config() -> Dict[str, Any]:
    """Retorna configuração de análise."""
    return ANALYSIS_CONFIG


def is_development() -> bool:
    """Verifica se está em modo desenvolvimento."""
    return os.getenv("ENVIRONMENT", "development").lower() == "development"


def is_production() -> bool:
    """Verifica se está em modo produção."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"