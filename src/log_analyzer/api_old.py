"""
API REST para o Log Analyzer - Versão Simplificada e Corrigida

Esta API fornece endpoints para análise de logs de segurança cibernética,
permitindo upload de arquivos de logs e retornando análises detalhadas
sobre ameaças detectadas, ataques de força bruta e varreduras de porta.
"""

import io
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
API_VERSION = "1.0.0"
API_NAME = "Log Analyzer API"
ERROR_MESSAGES = {
    "INTERNAL_ERROR": "Erro interno do servidor",
    "NO_FILES": "Pelo menos um arquivo de log deve ser enviado",
    "INVALID_FORMAT": "Formato de arquivo não suportado",
    "PROCESSING_ERROR": "Erro ao processar arquivo"
}

try:
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI não disponível. API não funcionará.")
    FASTAPI_AVAILABLE = False

try:
    from .core import LogAnalyzer
except ImportError:
    logger.error("LogAnalyzer não disponível")
    LogAnalyzer = None

# Criar aplicação FastAPI apenas se disponível
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title=API_NAME,
        description="API REST para análise de logs de segurança cibernética",
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None


@app.get("/")
async def status() -> Dict[str, str]:
    """
    Endpoint de status da API.
    
    Returns:
        Dict[str, str]: Status da API
    """
    return {"status": "Log Analyzer API is running"}


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        Dict[str, Any]: Informações sobre a saúde da API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "log-analyzer-api"
    }


class FileProcessor:
    """Classe para processar uploads de arquivos."""
    
    SUPPORTED_EXTENSIONS = {'.csv', '.json'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Valida um arquivo enviado."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
        
        extension = '.' + file.filename.split('.')[-1].lower()
        if extension not in FileProcessor.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {extension}"
            )
    
    @staticmethod
    def process_file(file: UploadFile) -> pd.DataFrame:
        """Processa um arquivo enviado e retorna DataFrame."""
        try:
            FileProcessor.validate_file(file)
            content = file.file.read()
            
            if len(content) > FileProcessor.MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="Arquivo muito grande")
            
            extension = '.' + file.filename.split('.')[-1].lower()
            
            if extension == '.csv':
                return FileProcessor._process_csv(content)
            elif extension == '.json':
                return FileProcessor._process_json(content)
            else:
                raise HTTPException(status_code=400, detail="Formato não suportado")
                
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
        for encoding in ['utf-8', 'utf-8-sig', 'latin1']:
            try:
                decoded_content = content.decode(encoding)
                return pd.read_csv(io.StringIO(decoded_content))
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        raise ValueError("Não foi possível processar o arquivo CSV")
    
    @staticmethod
    def _process_json(content: bytes) -> pd.DataFrame:
        """Processa arquivo JSON."""
        for encoding in ['utf-8', 'utf-8-sig']:
            try:
                decoded_content = content.decode(encoding)
                data = json.loads(decoded_content)
                
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    return pd.DataFrame([data])
                else:
                    raise ValueError("JSON deve ser uma lista ou objeto")
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        raise ValueError("Não foi possível processar o arquivo JSON")


class AnalysisManager:
    """Classe para gerenciar análises de logs."""
    
    def __init__(self, analyzer):
        """Inicializa o gerenciador com uma instância do analyzer."""
        self.analyzer = analyzer
    
    def process_files(self, firewall_log: Optional[UploadFile], auth_log: Optional[UploadFile]) -> Dict[str, int]:
        """Processa arquivos enviados."""
        files_processed = 0
        total_events = 0
        
        if firewall_log:
            firewall_df = FileProcessor.process_file(firewall_log)
            self.analyzer.data = firewall_df
            files_processed += 1
            total_events += len(firewall_df)
        
        if auth_log:
            auth_df = FileProcessor.process_file(auth_log)
            
            if self.analyzer.data is not None:
                self.analyzer.data = pd.concat([self.analyzer.data, auth_df], ignore_index=True)
            else:
                self.analyzer.data = auth_df
            
            files_processed += 1
            total_events += len(auth_df)
        
        return {"files_processed": files_processed, "total_events": total_events}
    
    def execute_analysis(self) -> Dict[str, Any]:
        """Executa todas as análises."""
        results = {
            "firewall_analysis": [],
            "brute_force_attacks": [],
            "authentication_failures": [],
            "geographic_analysis": [],
            "statistics": {},
            "top_suspicious_ips": [],
            "alerts": {"high_risk": [], "medium_risk": [], "low_risk": []}
        }
        
        if self.analyzer.data is None or self.analyzer.data.empty:
            return results
        
        # Análise de firewall
        firewall_results = self._safe_execute('analyze_firewall_logs', self.analyzer.data)
        if firewall_results is not None:
            results["firewall_analysis"] = self._dataframe_to_dict(firewall_results)
        
        # Análise de força bruta
        brute_force_results = self._safe_execute('analyze_brute_force')
        if brute_force_results is not None:
            results["brute_force_attacks"] = self._dataframe_to_dict(brute_force_results)
        
        # Estatísticas
        stats = self._safe_execute('generate_statistics')
        if stats:
            results["statistics"] = stats
        
        # IPs suspeitos
        results["top_suspicious_ips"] = self._extract_suspicious_ips()
        results["alerts"] = self._classify_alerts(results["top_suspicious_ips"])
        
        # Análise geográfica
        results["geographic_analysis"] = self._perform_geographic_analysis()
        
        return results
    
    def _safe_execute(self, method_name: str, *args, **kwargs) -> Any:
        """Executa um método de análise de forma segura."""
        try:
            method = getattr(self.analyzer, method_name, None)
            if method is None:
                return None
            return method(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Erro ao executar {method_name}: {str(e)}")
            return None
    
    def _dataframe_to_dict(self, df: pd.DataFrame) -> List[Dict]:
        """Converte DataFrame para lista de dicionários."""
        if df is None or df.empty:
            return []
        try:
            return df.to_dict('records')
        except Exception:
            return []
    
    def _extract_suspicious_ips(self) -> List[Dict[str, Any]]:
        """Extrai IPs suspeitos dos dados."""
        if 'source_ip' not in self.analyzer.data.columns:
            return []
        
        try:
            suspicious_ips = (self.analyzer.data['source_ip']
                            .value_counts()
                            .head(10)
                            .to_dict())
            
            return [
                {
                    "ip": ip, 
                    "occurrences": count,
                    "risk_level": self._classify_risk_level(count)
                }
                for ip, count in suspicious_ips.items()
            ]
        except Exception:
            return []
    
    def _classify_risk_level(self, count: int) -> str:
        """Classifica nível de risco baseado no número de ocorrências."""
        if count >= 10:
            return "high"
        elif count >= 5:
            return "medium"
        else:
            return "low"
    
    def _classify_alerts(self, suspicious_ips: List[Dict[str, Any]]) -> Dict[str, List]:
        """Classifica alertas por nível de risco."""
        alerts = {"high_risk": [], "medium_risk": [], "low_risk": []}
        
        for ip_data in suspicious_ips:
            risk_level = ip_data.get("risk_level", "low")
            if risk_level in alerts:
                alerts[risk_level].append(ip_data)
        
        return alerts
    
    def _perform_geographic_analysis(self) -> List[Dict[str, Any]]:
        """Executa análise geográfica se disponível."""
        try:
            from .geographic import GeographicAnalyzer
            
            geo_analyzer = GeographicAnalyzer()
            unique_ips = []
            
            if 'source_ip' in self.analyzer.data.columns:
                unique_ips.extend(self.analyzer.data['source_ip'].dropna().unique().tolist())
            
            if unique_ips:
                return geo_analyzer.analyze_ips(unique_ips[:10])
            
            return []
        except Exception as e:
            logger.warning(f"Análise geográfica falhou: {e}")
            return []


# Guardar as funções originais de forma segura
def _safe_analyze_method(analyzer, method_name: str, *args, **kwargs) -> Any:
    """Executa um método de análise de forma segura."""
    try:
        method = getattr(analyzer, method_name)
        return method(*args, **kwargs)
    except Exception as e:
        logging.warning(f"Erro ao executar {method_name}: {str(e)}")
        return None


def _process_uploaded_file(file: UploadFile) -> pd.DataFrame:
    """Processa um arquivo enviado e converte para DataFrame."""
    return FileProcessor.process_file(file)


def _dataframe_to_dict(df: pd.DataFrame) -> List[Dict]:
    """Converte DataFrame para lista de dicionários."""
    if df is None or df.empty:
        return []
    try:
        return df.to_dict('records')
    except Exception:
        return []


@app.post("/analyze/")
async def analyze_logs(
    firewall_log: Optional[UploadFile] = File(None),
    auth_log: Optional[UploadFile] = File(None)
) -> JSONResponse:
    """
    Endpoint principal para análise de logs de segurança.
    
    Este endpoint aceita uploads de arquivos de logs de firewall e/ou autenticação,
    executa análises abrangentes e retorna resultados consolidados sobre ameaças
    detectadas, ataques de força bruta, varreduras de porta e IPs suspeitos.
    
    Args:
        firewall_log: Arquivo de log do firewall (CSV ou JSON) - opcional
        auth_log: Arquivo de log de autenticação (CSV ou JSON) - opcional
        
    Returns:
        JSONResponse: Resultados consolidados da análise em formato JSON
        
    Raises:
        HTTPException: Se nenhum arquivo for enviado ou se houver erro no processamento
    """
    # Verificar se pelo menos um arquivo foi enviado
    if not firewall_log and not auth_log:
        raise HTTPException(
            status_code=400,
            detail="Pelo menos um arquivo de log deve ser enviado (firewall_log ou auth_log)"
        )
    
    try:
        # Criar instância do analisador
        analyzer = LogAnalyzer()
        
        # Resultados consolidados
        results = {
            "summary": {
                "files_processed": 0,
                "total_events": 0,
                "analysis_completed": True
            },
            "firewall_analysis": {},
            "brute_force_attacks": [],
            "authentication_failures": [],
            "geographic_analysis": [],
            "statistics": {},
            "top_suspicious_ips": [],
            "alerts": {
                "high_risk": [],
                "medium_risk": [],
                "low_risk": []
            }
        }
        
        # Processar arquivo de firewall se fornecido
        if firewall_log:
            try:
                firewall_df = _process_uploaded_file(firewall_log)
                analyzer.data = firewall_df
                results["summary"]["files_processed"] += 1
                results["summary"]["total_events"] += len(firewall_df)
                
                # Análise de logs de firewall
                firewall_results = _safe_analyze_method(analyzer, 'analyze_firewall_logs', firewall_df)
                if firewall_results:
                    results["firewall_analysis"] = _dataframe_to_dict(firewall_results)
                    
            except Exception as e:
                results["firewall_analysis"] = {"error": f"Erro ao processar firewall: {str(e)}"}
        
        # Processar arquivo de autenticação se fornecido
        if auth_log:
            try:
                auth_df = _process_uploaded_file(auth_log)
                
                # Se já temos dados do firewall, combinar; senão, usar apenas auth
                if analyzer.data is not None:
                    # Combinar dados se ambos os arquivos foram fornecidos
                    analyzer.data = pd.concat([analyzer.data, auth_df], ignore_index=True, sort=False)
                else:
                    analyzer.data = auth_df
                    
                results["summary"]["files_processed"] += 1
                results["summary"]["total_events"] += len(auth_df)
                
            except Exception as e:
                results["authentication_failures"] = {"error": f"Erro ao processar auth: {str(e)}"}
        
        # Executar análises se temos dados
        if analyzer.data is not None and not analyzer.data.empty:
            
            # Análise de força bruta
            brute_force_results = _safe_analyze_method(analyzer, 'analyze_brute_force')
            if brute_force_results is not None:
                results["brute_force_attacks"] = _dataframe_to_dict(brute_force_results)
            
            # Detecção de força bruta (método alternativo)
            try:
                analyzer.detect_brute_force(analyzer.data)
                if hasattr(analyzer, 'brute_force_attempts') and analyzer.brute_force_attempts:
                    results["brute_force_attacks"].extend(analyzer.brute_force_attempts)
            except Exception:
                pass
            
            # Gerar estatísticas
            stats = _safe_analyze_method(analyzer, 'generate_statistics')
            if stats:
                results["statistics"] = stats
            
            # Análise geográfica (se disponível)
            try:
                from .geographic import GeographicAnalyzer
                geo_analyzer = GeographicAnalyzer()
                
                # Extrair IPs únicos
                unique_ips = []
                if 'source_ip' in analyzer.data.columns:
                    unique_ips.extend(analyzer.data['source_ip'].dropna().unique().tolist())
                
                if unique_ips:
                    geo_results = geo_analyzer.analyze_ips(unique_ips[:10])  # Limitar a 10 IPs
                    results["geographic_analysis"] = geo_results
                    
            except Exception as e:
                results["geographic_analysis"] = {"error": f"Análise geográfica indisponível: {str(e)}"}
            
            # Identificar IPs mais suspeitos
            if 'source_ip' in analyzer.data.columns:
                suspicious_ips = (analyzer.data['source_ip']
                                .value_counts()
                                .head(10)
                                .to_dict())
                
                results["top_suspicious_ips"] = [
                    {"ip": ip, "occurrences": count} 
                    for ip, count in suspicious_ips.items()
                ]
                
                # Classificar por nível de risco
                for ip, count in suspicious_ips.items():
                    risk_entry = {"ip": ip, "occurrences": count}
                    
                    if count >= 10:
                        results["alerts"]["high_risk"].append(risk_entry)
                    elif count >= 5:
                        results["alerts"]["medium_risk"].append(risk_entry)
                    else:
                        results["alerts"]["low_risk"].append(risk_entry)
        
        # Adicionar metadados da análise
        results["metadata"] = {
            "api_version": "1.0.0",
            "analyzer_version": getattr(analyzer, 'version', '1.0.0'),
            "files_uploaded": [
                f.filename for f in [firewall_log, auth_log] if f is not None
            ]
        }
        
        return JSONResponse(
            content=results,
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante a análise: {str(e)}"
        )


@app.get("/api-info")
async def api_info() -> Dict[str, Any]:
    """
    Informações sobre a API e seus endpoints.
    
    Returns:
        Dict[str, Any]: Informações detalhadas sobre a API
    """
    return {
        "name": "Log Analyzer API",
        "version": "1.0.0",
        "description": "API REST para análise de logs de segurança cibernética",
        "endpoints": {
            "/": "Status da API",
            "/health": "Verificação de saúde",
            "/analyze/": "Análise de logs (POST com upload de arquivos)",
            "/api-info": "Informações sobre a API",
            "/docs": "Documentação interativa (Swagger)",
            "/redoc": "Documentação alternativa (ReDoc)"
        },
        "supported_formats": ["CSV", "JSON"],
        "supported_log_types": ["firewall", "authentication"],
        "features": [
            "Detecção de ataques de força bruta",
            "Análise de varreduras de porta",
            "Análise geográfica de IPs",
            "Classificação de riscos",
            "Estatísticas detalhadas",
            "Identificação de IPs suspeitos"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "log_analyzer.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )