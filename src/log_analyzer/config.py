"""
Configurações padrão do Log Analyzer
"""

# Configurações de detecção de ameaças
DEFAULT_CONFIG = {
    # Brute Force Detection
    "brute_force": {
        "threshold": 5,  # Número mínimo de tentativas
        "time_window_minutes": 1,  # Janela de tempo em minutos
    },
    
    # Port Scanning Detection  
    "port_scan": {
        "threshold": 10,  # Número mínimo de portas
        "time_window_minutes": 1,  # Janela de tempo em minutos
    },
    
    # Geographic Analysis
    "geographic": {
        "enabled": True,  # Habilitar análise geográfica por padrão
        "timeout_seconds": 5,  # Timeout para requisições
        "api_url": "http://ip-api.com/json",  # API de geolocalização
        "rate_limit_delay": 1.5,  # Delay entre requisições (segundos)
        "high_risk_countries": ["CN", "RU", "KP", "IR", "BY"],  # Países de alto risco
    },
    
    # Risk Classification
    "risk_classification": {
        "high_threshold": 10,  # Número de acessos para alto risco
        "medium_threshold": 5,  # Número de acessos para médio risco
    },
    
    # Export Settings
    "export": {
        "default_filename": "suspect_ips.csv",
        "auto_timestamp": True,  # Adicionar timestamp ao nome do arquivo
    },
    
    # Logging
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "log_analyzer.log",
    }
}

# Esquemas de dados suportados
SUPPORTED_SCHEMAS = {
    "firewall": {
        "required_columns": ["timestamp", "source_ip", "destination_ip", "port", "protocol", "action"],
        "optional_columns": ["destination_port", "bytes", "packets"]
    },
    
    "authentication": {
        "required_columns": ["timestamp", "source_ip", "username", "service", "status"],
        "optional_columns": ["destination_ip", "session_id", "user_agent"]
    }
}

# Formatos de data suportados
SUPPORTED_DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%d/%m/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
]