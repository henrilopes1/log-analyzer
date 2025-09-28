"""
Utilitários do Log Analyzer
"""

import os
import logging
import json
from datetime import datetime
from typing import Union, Dict, Any, List, Optional
import pandas as pd
from pathlib import Path

from .config import DEFAULT_CONFIG, SUPPORTED_DATE_FORMATS


def setup_logging(config: Dict[str, Any] = None) -> logging.Logger:
    """
    Configura o sistema de logging
    
    Args:
        config: Configurações de logging (opcional)
        
    Returns:
        Logger configurado
    """
    if config is None:
        config = DEFAULT_CONFIG["logging"]
    
    logging.basicConfig(
        level=getattr(logging, config["level"]),
        format=config["format"],
        handlers=[
            logging.FileHandler(config["file"]),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("log_analyzer")


def validate_file_format(file_path: str) -> str:
    """
    Valida o formato do arquivo de log
    
    Args:
        file_path: Caminho para o arquivo
        
    Returns:
        Formato do arquivo ('csv' ou 'json')
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
        ValueError: Se o formato não for suportado
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.csv':
        return 'csv'
    elif file_extension == '.json':
        return 'json'
    else:
        raise ValueError(f"Formato de arquivo não suportado: {file_extension}")


def load_data_file(file_path: str) -> pd.DataFrame:
    """
    Carrega arquivo de dados (CSV ou JSON)
    
    Args:
        file_path: Caminho para o arquivo
        
    Returns:
        DataFrame com os dados carregados
        
    Raises:
        Exception: Se houver erro no carregamento
    """
    file_format = validate_file_format(file_path)
    
    try:
        if file_format == 'csv':
            df = pd.read_csv(file_path)
        else:  # json
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            df = pd.DataFrame(json_data)
        
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao carregar arquivo {file_path}: {str(e)}")


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Converte string de timestamp para datetime
    
    Args:
        timestamp_str: String com timestamp
        
    Returns:
        Objeto datetime ou None se não conseguir converter
    """
    for date_format in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(timestamp_str, date_format)
        except ValueError:
            continue
    
    return None


def ensure_directory_exists(directory_path: str) -> None:
    """
    Garante que um diretório existe, criando-o se necessário
    
    Args:
        directory_path: Caminho para o diretório
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def generate_timestamped_filename(base_filename: str) -> str:
    """
    Gera um nome de arquivo com timestamp
    
    Args:
        base_filename: Nome base do arquivo
        
    Returns:
        Nome do arquivo com timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, extension = os.path.splitext(base_filename)
    return f"{name}_{timestamp}{extension}"


def validate_required_columns(df: pd.DataFrame, required_columns: List[str], 
                            file_type: str) -> bool:
    """
    Valida se o DataFrame possui as colunas obrigatórias
    
    Args:
        df: DataFrame para validar
        required_columns: Lista de colunas obrigatórias
        file_type: Tipo do arquivo para mensagens de erro
        
    Returns:
        True se válido
        
    Raises:
        ValueError: Se colunas obrigatórias estiverem faltando
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes no arquivo {file_type}: "
            f"{', '.join(missing_columns)}"
        )
    
    return True


def clean_ip_address(ip: str) -> str:
    """
    Limpa e valida endereço IP
    
    Args:
        ip: Endereço IP para limpar
        
    Returns:
        IP limpo ou string vazia se inválido
    """
    if not ip or pd.isna(ip):
        return ""
    
    # Remover espaços e converter para string
    ip = str(ip).strip()
    
    # Validação básica de formato IPv4
    parts = ip.split('.')
    if len(parts) == 4:
        try:
            for part in parts:
                num = int(part)
                if not (0 <= num <= 255):
                    return ""
            return ip
        except ValueError:
            return ""
    
    return ""


def format_duration(seconds: float) -> str:
    """
    Formata duração em segundos para string legível
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        String formatada (ex: "2m 30s", "45s")
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def calculate_risk_score(ip_data: Dict[str, Any]) -> int:
    """
    Calcula pontuação de risco para um IP
    
    Args:
        ip_data: Dicionário com dados do IP
        
    Returns:
        Pontuação de risco (0-100)
    """
    score = 0
    
    # Pontuação base por número de tentativas
    attempts = ip_data.get('attempts', 0)
    score += min(attempts * 5, 50)  # Max 50 pontos
    
    # Bonificação por tipo de ataque
    if ip_data.get('brute_force', False):
        score += 25
    
    if ip_data.get('port_scan', False):
        score += 20
    
    # Bonificação por localização geográfica
    if ip_data.get('high_risk_country', False):
        score += 15
    
    if ip_data.get('using_vpn', False):
        score += 10
    
    return min(score, 100)  # Max 100 pontos