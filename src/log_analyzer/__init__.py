"""
Log Analyzer - Ferramenta de Análise de Segurança
================================================

Uma ferramenta Python avançada para análise de logs de segurança com suporte
a CSV e JSON, detecção de ataques e análise geográfica.

Autor: Security Team
Versão: 2.0
Data: Dezembro 2024
"""

__version__ = "2.0.0"
__author__ = "Security Team"
__description__ = "Ferramenta de análise de logs de segurança"

from .core import LogAnalyzer
from .utils import setup_logging, validate_file_format
from .config import DEFAULT_CONFIG
from .main import main

__all__ = ['LogAnalyzer', 'setup_logging', 'validate_file_format', 'DEFAULT_CONFIG', 'main']

__all__ = [
    'LogAnalyzer',
    'setup_logging', 
    'validate_file_format',
    'DEFAULT_CONFIG'
]