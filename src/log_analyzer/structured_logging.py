"""
Sistema de Logging Estruturado para o Log Analyzer
Implementa logging JSON estruturado com contexto e métricas
"""

import logging
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from contextvars import ContextVar
import traceback


# Context variables para rastreamento de requisições
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Formata log record como JSON estruturado."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }

        # Adicionar contexto de requisição se disponível
        request_id = request_id_var.get("")
        if request_id:
            log_entry["request_id"] = request_id

        user_id = user_id_var.get("")
        if user_id:
            log_entry["user_id"] = user_id

        # Adicionar informações extras se disponíveis
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data

        # Adicionar stack trace se for erro
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Adicionar métricas de performance se disponíveis
        if hasattr(record, "performance"):
            log_entry["performance"] = record.performance

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class PerformanceLogger:
    """Logger para métricas de performance."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_request(
        self, method: str, path: str, status_code: int, duration_ms: float, **kwargs
    ):
        """Loga requisição HTTP."""
        extra_data = {
            "event_type": "http_request",
            "http_method": method,
            "http_path": path,
            "http_status": status_code,
            "duration_ms": duration_ms,
            **kwargs,
        }

        self.logger.info(
            f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
            extra={"extra_data": extra_data},
        )

    def log_function_call(
        self, function_name: str, duration_ms: float, success: bool = True, **kwargs
    ):
        """Loga execução de função."""
        extra_data = {
            "event_type": "function_call",
            "function_name": function_name,
            "duration_ms": duration_ms,
            "success": success,
            **kwargs,
        }

        level = logging.INFO if success else logging.ERROR
        message = f"Function {function_name} executed in {duration_ms:.2f}ms"

        self.logger.log(level, message, extra={"extra_data": extra_data})

    def log_database_query(
        self, query_type: str, duration_ms: float, rows_affected: int = 0, **kwargs
    ):
        """Loga query de banco de dados."""
        extra_data = {
            "event_type": "database_query",
            "query_type": query_type,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            **kwargs,
        }

        self.logger.info(
            f"DB query {query_type} executed in {duration_ms:.2f}ms",
            extra={"extra_data": extra_data},
        )


class SecurityLogger:
    """Logger para eventos de segurança."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_authentication(
        self, user_id: str, success: bool, ip_address: str = None, **kwargs
    ):
        """Loga tentativa de autenticação."""
        extra_data = {
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            **kwargs,
        }

        level = logging.INFO if success else logging.WARNING
        message = (
            f"Authentication {'successful' if success else 'failed'} for user {user_id}"
        )

        self.logger.log(level, message, extra={"extra_data": extra_data})

    def log_authorization(
        self, user_id: str, resource: str, action: str, success: bool, **kwargs
    ):
        """Loga tentativa de autorização."""
        extra_data = {
            "event_type": "authorization",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "success": success,
            **kwargs,
        }

        level = logging.INFO if success else logging.WARNING
        message = f"Authorization {'granted' if success else 'denied'} for {user_id} on {resource}:{action}"

        self.logger.log(level, message, extra={"extra_data": extra_data})

    def log_security_event(
        self, event_type: str, severity: str, description: str, **kwargs
    ):
        """Loga evento de segurança."""
        extra_data = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "description": description,
            **kwargs,
        }

        level_map = {
            "low": logging.INFO,
            "medium": logging.WARNING,
            "high": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        level = level_map.get(severity.lower(), logging.INFO)
        message = f"Security event: {event_type} - {description}"

        self.logger.log(level, message, extra={"extra_data": extra_data})


class BusinessLogger:
    """Logger para eventos de negócio."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_analysis_started(self, file_name: str, file_size: int, **kwargs):
        """Loga início de análise."""
        extra_data = {
            "event_type": "analysis_started",
            "file_name": file_name,
            "file_size_bytes": file_size,
            **kwargs,
        }

        self.logger.info(
            f"Analysis started for file {file_name} ({file_size} bytes)",
            extra={"extra_data": extra_data},
        )

    def log_analysis_completed(
        self, file_name: str, duration_ms: float, results_count: int, **kwargs
    ):
        """Loga conclusão de análise."""
        extra_data = {
            "event_type": "analysis_completed",
            "file_name": file_name,
            "duration_ms": duration_ms,
            "results_count": results_count,
            **kwargs,
        }

        self.logger.info(
            f"Analysis completed for {file_name} in {duration_ms:.2f}ms with {results_count} results",
            extra={"extra_data": extra_data},
        )

    def log_threat_detected(
        self, threat_type: str, severity: str, source_ip: str = None, **kwargs
    ):
        """Loga detecção de ameaça."""
        extra_data = {
            "event_type": "threat_detected",
            "threat_type": threat_type,
            "severity": severity,
            "source_ip": source_ip,
            **kwargs,
        }

        level_map = {
            "low": logging.INFO,
            "medium": logging.WARNING,
            "high": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        level = level_map.get(severity.lower(), logging.WARNING)
        message = (
            f"Threat detected: {threat_type} ({severity}) from {source_ip or 'unknown'}"
        )

        self.logger.log(level, message, extra={"extra_data": extra_data})


def setup_structured_logging(
    name: str = "log_analyzer", level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """Configura sistema de logging estruturado."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remover handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Formatter estruturado
    formatter = StructuredFormatter()

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para arquivo se especificado
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "log_analyzer") -> logging.Logger:
    """Retorna logger configurado."""
    return logging.getLogger(name)


def set_request_context(request_id: str = None, user_id: str = None):
    """Define contexto da requisição atual."""
    if request_id is None:
        request_id = str(uuid.uuid4())

    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context():
    """Limpa contexto da requisição."""
    request_id_var.set("")
    user_id_var.set("")


# Configurar logger principal
main_logger = setup_structured_logging()

# Instâncias especializadas
performance_logger = PerformanceLogger(main_logger)
security_logger = SecurityLogger(main_logger)
business_logger = BusinessLogger(main_logger)
