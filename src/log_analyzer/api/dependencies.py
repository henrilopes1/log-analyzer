"""
Dependências da API
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException

from ..core import LogAnalyzer


# Configuração de logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Instância global do analisador
_analyzer_instance: Optional[LogAnalyzer] = None
_start_time = datetime.now(timezone.utc)


def get_start_time() -> datetime:
    """Retorna o horário de início da aplicação."""
    return _start_time


def get_analyzer() -> LogAnalyzer:
    """
    Dependência para obter instância do LogAnalyzer.
    
    Returns:
        LogAnalyzer: Instância configurada do analisador
        
    Raises:
        HTTPException: Se não for possível criar o analisador
    """
    global _analyzer_instance
    
    if _analyzer_instance is None:
        try:
            _analyzer_instance = LogAnalyzer()
            logger.info("LogAnalyzer instance created successfully")
        except Exception as e:
            logger.error(f"Failed to create LogAnalyzer instance: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno: Não foi possível inicializar o analisador - {str(e)}"
            ) from e
    
    return _analyzer_instance


def reset_analyzer() -> None:
    """
    Reset da instância do analisador (útil para testes).
    """
    global _analyzer_instance
    _analyzer_instance = None


class AnalyzerDependency:
    """Classe de dependência para o LogAnalyzer com configurações personalizadas."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config
    
    def __call__(self) -> LogAnalyzer:
        """
        Cria uma nova instância do LogAnalyzer com configuração personalizada.
        
        Returns:
            LogAnalyzer: Nova instância configurada
        """
        try:
            return LogAnalyzer(config=self.config)
        except Exception as e:
            logger.error(f"Failed to create LogAnalyzer with custom config: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno: Configuração inválida do analisador - {str(e)}"
            ) from e


def get_custom_analyzer(config: dict) -> AnalyzerDependency:
    """
    Factory para criar dependência com configuração personalizada.
    
    Args:
        config: Configuração personalizada
        
    Returns:
        AnalyzerDependency: Dependência configurada
    """
    return AnalyzerDependency(config)