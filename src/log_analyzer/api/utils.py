"""
Utilitários para processamento de arquivos na API
"""

import io
import json
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class FileProcessor:
    """Classe para processar uploads de arquivos."""
    
    SUPPORTED_EXTENSIONS = {'.csv', '.json'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @classmethod
    def validate_file(cls, file: UploadFile) -> None:
        """
        Valida um arquivo enviado.
        
        Args:
            file: Arquivo enviado
            
        Raises:
            HTTPException: Se o arquivo for inválido
        """
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Nome do arquivo é obrigatório"
            )
        
        # Verificar extensão
        extension = '.' + file.filename.split('.')[-1].lower()
        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {extension}. "
                       f"Formatos aceitos: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
    
    @classmethod
    def process_file(cls, file: UploadFile) -> pd.DataFrame:
        """
        Processa um arquivo enviado e retorna DataFrame.
        
        Args:
            file: Arquivo enviado
            
        Returns:
            pd.DataFrame: Dados do arquivo
            
        Raises:
            HTTPException: Se não for possível processar o arquivo
        """
        try:
            cls.validate_file(file)
            
            # Ler conteúdo
            content = file.file.read()
            
            if len(content) > cls.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Arquivo muito grande. Tamanho máximo: {cls.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Resetar posição do arquivo
            file.file.seek(0)
            
            # Processar baseado na extensão
            extension = '.' + file.filename.split('.')[-1].lower()
            
            if extension == '.csv':
                return cls._process_csv(content)
            elif extension == '.json':
                return cls._process_json(content)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Processador não disponível para {extension}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file.filename}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar arquivo: {str(e)}"
            ) from e
    
    @staticmethod
    def _process_csv(content: bytes) -> pd.DataFrame:
        """Processa arquivo CSV."""
        try:
            # Tentar diferentes encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
                try:
                    decoded_content = content.decode(encoding)
                    return pd.read_csv(io.StringIO(decoded_content))
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Não foi possível decodificar o arquivo CSV")
            
        except Exception as e:
            raise ValueError(f"Erro ao processar CSV: {str(e)}") from e
    
    @staticmethod
    def _process_json(content: bytes) -> pd.DataFrame:
        """Processa arquivo JSON."""
        try:
            # Tentar diferentes encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin1']:
                try:
                    decoded_content = content.decode(encoding)
                    data = json.loads(decoded_content)
                    
                    if isinstance(data, list):
                        return pd.DataFrame(data)
                    elif isinstance(data, dict):
                        # Se for um dict, tentar usar como uma linha
                        return pd.DataFrame([data])
                    else:
                        raise ValueError("JSON deve ser uma lista de objetos ou um objeto")
                        
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Não foi possível decodificar o arquivo JSON")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Erro ao processar JSON: {str(e)}") from e


class AnalysisProcessor:
    """Classe para processar análises de logs."""
    
    @staticmethod
    def safe_execute_analysis(analyzer, method_name: str, *args, **kwargs) -> Any:
        """
        Executa um método de análise de forma segura.
        
        Args:
            analyzer: Instância do LogAnalyzer
            method_name: Nome do método a ser executado
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Any: Resultado do método ou None se houver erro
        """
        try:
            method = getattr(analyzer, method_name, None)
            if method is None:
                logger.warning(f"Método {method_name} não encontrado no analyzer")
                return None
                
            return method(*args, **kwargs)
            
        except Exception as e:
            logger.warning(f"Erro ao executar {method_name}: {str(e)}")
            return None
    
    @staticmethod
    def dataframe_to_records(df: Optional[pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Converte DataFrame para lista de dicionários.
        
        Args:
            df: DataFrame a ser convertido
            
        Returns:
            List[Dict]: Lista de registros
        """
        if df is None or df.empty:
            return []
        
        try:
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Erro ao converter DataFrame: {e}")
            return []
    
    @staticmethod
    def extract_suspicious_ips(data: pd.DataFrame, threshold: int = 5) -> List[Dict[str, Any]]:
        """
        Extrai IPs suspeitos dos dados.
        
        Args:
            data: DataFrame com os dados
            threshold: Limite mínimo de ocorrências
            
        Returns:
            List[Dict]: Lista de IPs suspeitos
        """
        if data is None or data.empty:
            return []
        
        try:
            # Procurar por colunas de IP comuns
            ip_columns = ['source_ip', 'src_ip', 'ip', 'client_ip']
            ip_column = None
            
            for col in ip_columns:
                if col in data.columns:
                    ip_column = col
                    break
            
            if ip_column is None:
                return []
            
            # Contar ocorrências
            ip_counts = data[ip_column].value_counts()
            suspicious = ip_counts[ip_counts >= threshold]
            
            return [
                {
                    "ip": ip,
                    "occurrences": int(count),
                    "risk_level": AnalysisProcessor._classify_risk(count)
                }
                for ip, count in suspicious.items()
            ]
            
        except Exception as e:
            logger.error(f"Erro ao extrair IPs suspeitos: {e}")
            return []
    
    @staticmethod
    def _classify_risk(occurrences: int) -> str:
        """Classifica nível de risco baseado no número de ocorrências."""
        if occurrences >= 10:
            return "high"
        elif occurrences >= 5:
            return "medium"
        else:
            return "low"