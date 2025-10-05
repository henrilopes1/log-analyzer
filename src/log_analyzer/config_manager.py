"""
Sistema de configuração avançada para o Log Analyzer
Gerencia configurações através de variáveis de ambiente e arquivos
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class DatabaseConfig:
    """Configuração de banco de dados."""

    url: str = "sqlite:///logs.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class RedisConfig:
    """Configuração do Redis para cache."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ttl_seconds: int = 3600


@dataclass
class SecurityConfig:
    """Configuração de segurança."""

    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allowed_hosts: Optional[List[str]] = None
    cors_origins: Optional[List[str]] = None


@dataclass
class AppConfig:
    """Configuração principal da aplicação."""

    name: str = "Log Analyzer"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Sub-configurações
    database: Optional[DatabaseConfig] = None
    redis: Optional[RedisConfig] = None
    security: Optional[SecurityConfig] = None

    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.redis is None:
            self.redis = RedisConfig()
        if self.security is None:
            self.security = SecurityConfig()


class ConfigManager:
    """Gerenciador de configurações."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config = None

    def load_config(self) -> AppConfig:
        """Carrega configuração de múltiplas fontes."""
        config_data = {}

        # 1. Carregar de arquivo se especificado
        if self.config_file and Path(self.config_file).exists():
            config_data.update(self._load_from_file(self.config_file))

        # 2. Carregar de variáveis de ambiente
        config_data.update(self._load_from_env())

        # 3. Aplicar defaults e criar objeto
        self._config = self._create_config(config_data)
        return self._config

    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Carrega configuração de arquivo (JSON ou YAML)."""
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() in [".yml", ".yaml"]:
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar arquivo de configuração {file_path}: {e}")
            return {}

    def _load_from_env(self) -> Dict[str, Any]:
        """Carrega configuração de variáveis de ambiente."""
        config = {}

        # Mapeamento de variáveis de ambiente
        env_mapping = {
            # App
            "LOG_ANALYZER_DEBUG": ("debug", bool),
            "LOG_ANALYZER_HOST": ("host", str),
            "LOG_ANALYZER_PORT": ("port", int),
            "LOG_ANALYZER_WORKERS": ("workers", int),
            "LOG_ANALYZER_ENVIRONMENT": ("environment", str),
            # Database
            "DATABASE_URL": ("database.url", str),
            "DATABASE_ECHO": ("database.echo", bool),
            # Redis
            "REDIS_HOST": ("redis.host", str),
            "REDIS_PORT": ("redis.port", int),
            "REDIS_PASSWORD": ("redis.password", str),
            # Security
            "SECRET_KEY": ("security.secret_key", str),
            "ACCESS_TOKEN_EXPIRE_MINUTES": (
                "security.access_token_expire_minutes",
                int,
            ),
        }

        for env_var, (config_path, config_type) in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Converter tipo
                if config_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif config_type == int:
                    try:
                        value = int(value)
                    except ValueError:
                        continue

                # Aplicar no config usando notação de ponto
                self._set_nested_value(config, config_path, value)

        return config

    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any):
        """Define valor em estrutura aninhada usando notação de ponto."""
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _create_config(self, config_data: Dict[str, Any]) -> AppConfig:
        """Cria objeto de configuração."""
        # Extrair configurações aninhadas
        database_config = DatabaseConfig(**config_data.get("database", {}))
        redis_config = RedisConfig(**config_data.get("redis", {}))
        security_config = SecurityConfig(**config_data.get("security", {}))

        # Remover configurações aninhadas dos dados principais
        main_config = {
            k: v
            for k, v in config_data.items()
            if k not in ["database", "redis", "security"]
        }

        return AppConfig(
            **main_config,
            database=database_config,
            redis=redis_config,
            security=security_config,
        )

    def save_config(self, file_path: str, format: str = "yaml"):
        """Salva configuração atual em arquivo."""
        if self._config is None:
            raise ValueError("Nenhuma configuração carregada")

        config_dict = asdict(self._config)

        with open(file_path, "w", encoding="utf-8") as f:
            if format.lower() == "yaml":
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_dict, f, indent=2)

    def get_config(self) -> AppConfig:
        """Retorna configuração atual."""
        if self._config is None:
            return self.load_config()
        return self._config


# Instância global do gerenciador de configurações
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Retorna configuração global."""
    return config_manager.get_config()
