"""
API REST para o Log Analyzer - Versão Premium

Esta API fornece endpoints para análise de logs de segurança cibernética.
Aplicando boas práticas de programação, monitoramento e otimização.
"""

import io
import json
import logging
import os
import time
import psutil
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from functools import wraps

import pandas as pd

# Configuração de logging avançada
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/api.log", mode="a") if os.path.exists("logs") else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constantes
API_VERSION = "1.0.0"
API_NAME = "Log Analyzer API"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_FORMATS = [".csv", ".json"]

# Importações condicionais para robustez
try:
    from fastapi import FastAPI, File, HTTPException, UploadFile, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"FastAPI não disponível: {e}")
    FASTAPI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil não disponível")
    PSUTIL_AVAILABLE = False

try:
    from .core import LogAnalyzer

    CORE_AVAILABLE = True
except ImportError:
    logger.error("LogAnalyzer core não disponível")
    CORE_AVAILABLE = False


class PerformanceMonitor:
    """Monitor de performance e métricas da API."""
    
    def __init__(self):
        self.request_count = 0
        self.total_response_time = 0
        self.start_time = time.time()
    
    def record_request(self, response_time: float):
        """Registra uma requisição."""
        self.request_count += 1
        self.total_response_time += response_time
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais."""
        uptime = time.time() - self.start_time
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        metrics = {
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "avg_response_time_ms": avg_response_time * 1000,
            "requests_per_second": self.request_count / uptime if uptime > 0 else 0,
        }
        
        # Adicionar métricas do sistema se psutil disponível
        if PSUTIL_AVAILABLE:
            metrics.update({
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
            })
        
        return metrics


class MetricsMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Middleware para coleta de métricas."""
    
    def __init__(self, app, monitor: PerformanceMonitor):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.monitor = monitor
    
    async def dispatch(self, request: "Request", call_next):
        """Processa requisição e coleta métricas."""
        if not FASTAPI_AVAILABLE:
            return await call_next(request)
            
        start_time = time.time()
        
        try:
            response = await call_next(request)
            response_time = time.time() - start_time
            self.monitor.record_request(response_time)
            
            # Adicionar headers de performance
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            response.headers["X-Request-ID"] = str(self.monitor.request_count)
            
            return response
        except Exception as e:
            response_time = time.time() - start_time
            self.monitor.record_request(response_time)
            logger.error(f"Erro na requisição: {e}")
            raise


# Instância global de monitoramento
performance_monitor = PerformanceMonitor()


class FileHandler:
    """Manipula operações de arquivo de forma segura."""

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Valida arquivo enviado."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo obrigatório")

        extension = "." + file.filename.split(".")[-1].lower()
        if extension not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400, detail=f"Formato não suportado: {extension}"
            )

    @staticmethod
    def process_file(file: UploadFile) -> pd.DataFrame:
        """Processa arquivo e retorna DataFrame."""
        FileHandler.validate_file(file)

        try:
            content = file.file.read()

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="Arquivo muito grande")

            extension = "." + file.filename.split(".")[-1].lower()

            if extension == ".csv":
                return FileHandler._process_csv(content)
            elif extension == ".json":
                return FileHandler._process_json(content)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro processar arquivo {file.filename}: {e}")
            raise HTTPException(status_code=400, detail=str(e)) from e

    @staticmethod
    def _process_csv(content: bytes) -> pd.DataFrame:
        """Processa conteúdo CSV."""
        for encoding in ["utf-8", "utf-8-sig", "latin1"]:
            try:
                decoded = content.decode(encoding)
                return pd.read_csv(io.StringIO(decoded))
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        raise ValueError("Não foi possível processar CSV")

    @staticmethod
    def _process_json(content: bytes) -> pd.DataFrame:
        """Processa conteúdo JSON."""
        for encoding in ["utf-8", "utf-8-sig"]:
            try:
                decoded = content.decode(encoding)
                data = json.loads(decoded)

                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    return pd.DataFrame([data])
                else:
                    raise ValueError("JSON deve ser lista ou objeto")
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        raise ValueError("Não foi possível processar JSON")


class AnalysisService:
    """Serviço de análise de logs."""

    def __init__(self):
        """Inicializa o serviço."""
        if not CORE_AVAILABLE:
            raise RuntimeError("LogAnalyzer core não disponível")
        self.analyzer = LogAnalyzer()

    def analyze_files(
        self, firewall_log: Optional[UploadFile], auth_log: Optional[UploadFile]
    ) -> Dict[str, Any]:
        """Analisa arquivos de log enviados."""
        start_time = time.time()

        # Processar arquivos
        file_info = self._process_files(firewall_log, auth_log)

        # Executar análise
        results = self._execute_analysis()

        # Preparar resposta
        return self._prepare_response(
            results, file_info, start_time, firewall_log, auth_log
        )

    def _process_files(
        self, firewall_log: Optional[UploadFile], auth_log: Optional[UploadFile]
    ) -> Dict[str, int]:
        """Processa arquivos enviados."""
        files_processed = 0
        total_events = 0

        if firewall_log:
            df = FileHandler.process_file(firewall_log)
            self.analyzer.data = df
            files_processed += 1
            total_events += len(df)

        if auth_log:
            df = FileHandler.process_file(auth_log)
            if self.analyzer.data is not None:
                self.analyzer.data = pd.concat(
                    [self.analyzer.data, df], ignore_index=True
                )
            else:
                self.analyzer.data = df
            files_processed += 1
            total_events += len(df)

        return {"files_processed": files_processed, "total_events": total_events}

    def _execute_analysis(self) -> Dict[str, Any]:
        """Executa análises nos dados."""
        results = {
            "firewall_analysis": [],
            "brute_force_attacks": [],
            "statistics": {},
            "top_suspicious_ips": [],
            "alerts": {"high_risk": [], "medium_risk": [], "low_risk": []},
            "geographic_analysis": [],
        }

        if self.analyzer.data is None or self.analyzer.data.empty:
            return results

        # Análises básicas
        results["firewall_analysis"] = self._safe_analysis(
            "analyze_firewall_logs", self.analyzer.data
        )
        results["brute_force_attacks"] = self._safe_analysis("analyze_brute_force")
        results["statistics"] = self._safe_analysis("generate_statistics") or {}

        # IPs suspeitos
        results["top_suspicious_ips"] = self._extract_suspicious_ips()
        results["alerts"] = self._classify_alerts(results["top_suspicious_ips"])

        # Análise geográfica
        results["geographic_analysis"] = self._geographic_analysis()

        return results

    def _safe_analysis(self, method_name: str, *args) -> Any:
        """Executa análise de forma segura."""
        try:
            method = getattr(self.analyzer, method_name, None)
            if method is None:
                return None

            result = method(*args)

            # Converter DataFrame para dict se necessário
            if isinstance(result, pd.DataFrame):
                return result.to_dict("records") if not result.empty else []

            return result
        except Exception as e:
            logger.warning(f"Erro em {method_name}: {e}")
            return None

    def _extract_suspicious_ips(self) -> List[Dict[str, Any]]:
        """Extrai IPs suspeitos."""
        if "source_ip" not in self.analyzer.data.columns:
            return []

        try:
            ip_counts = self.analyzer.data["source_ip"].value_counts().head(10)
            return [
                {
                    "ip": ip,
                    "occurrences": int(count),
                    "risk_level": self._risk_level(count),
                }
                for ip, count in ip_counts.items()
            ]
        except Exception as e:
            logger.warning(f"Erro extrair IPs: {e}")
            return []

    def _risk_level(self, count: int) -> str:
        """Classifica nível de risco."""
        if count >= 10:
            return "high"
        elif count >= 5:
            return "medium"
        return "low"

    def _classify_alerts(self, suspicious_ips: List[Dict[str, Any]]) -> Dict[str, List]:
        """Classifica alertas por risco."""
        alerts = {"high_risk": [], "medium_risk": [], "low_risk": []}

        for ip_data in suspicious_ips:
            risk = ip_data.get("risk_level", "low")
            if risk in alerts:
                alerts[risk].append(ip_data)

        return alerts

    def _geographic_analysis(self) -> List[Dict[str, Any]]:
        """Análise geográfica."""
        try:
            from .geographic import GeographicAnalyzer

            geo = GeographicAnalyzer()
            unique_ips = []

            if "source_ip" in self.analyzer.data.columns:
                unique_ips = self.analyzer.data["source_ip"].dropna().unique().tolist()

            if unique_ips:
                return geo.analyze_ips(unique_ips[:10])

            return []
        except Exception as e:
            logger.warning(f"Análise geográfica falhou: {e}")
            return []

    def _prepare_response(
        self,
        results: Dict[str, Any],
        file_info: Dict[str, int],
        start_time: float,
        firewall_log: Optional[UploadFile],
        auth_log: Optional[UploadFile],
    ) -> Dict[str, Any]:
        """Prepara resposta final."""
        processing_time = time.time() - start_time

        return {
            "summary": {
                **file_info,
                "analysis_completed": True,
                "processing_time_seconds": processing_time,
            },
            **results,
            "metadata": {
                "api_version": API_VERSION,
                "analyzer_version": "1.0.0",
                "files_uploaded": [
                    f.filename for f in [firewall_log, auth_log] if f is not None
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }


# Criar aplicação FastAPI
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title=API_NAME,
        description="API REST para análise de logs de segurança cibernética",
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware de métricas
    app.add_middleware(MetricsMiddleware, monitor=performance_monitor)

    @app.get("/")
    async def status() -> Dict[str, str]:
        """Status da API."""
        return {
            "status": "Log Analyzer API is running",
            "version": API_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        """Health check avançado."""
        health_status = {
            "status": "healthy",
            "version": API_VERSION,
            "service": "log-analyzer-api",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "core": "available" if CORE_AVAILABLE else "unavailable",
                "fastapi": "available" if FASTAPI_AVAILABLE else "unavailable",
                "psutil": "available" if PSUTIL_AVAILABLE else "unavailable",
            },
        }
        
        # Verificar saúde do sistema
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 90 or memory_percent > 90:
                health_status["status"] = "degraded"
                health_status["warnings"] = []
                if cpu_percent > 90:
                    health_status["warnings"].append(f"High CPU usage: {cpu_percent}%")
                if memory_percent > 90:
                    health_status["warnings"].append(f"High memory usage: {memory_percent}%")
        
        return health_status
    
    @app.get("/metrics")
    async def metrics() -> Dict[str, Any]:
        """Métricas de performance da API."""
        return {
            "metrics": performance_monitor.get_metrics(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/api-info")
    async def api_info() -> Dict[str, Any]:
        """Informações da API."""
        return {
            "name": API_NAME,
            "version": API_VERSION,
            "description": "API REST para análise de logs de segurança",
            "endpoints": {
                "/": "Status da API",
                "/health": "Health check",
                "/analyze/": "Análise de logs",
                "/api-info": "Informações da API",
            },
            "supported_formats": ["CSV", "JSON"],
            "features": [
                "Detecção de força bruta",
                "Análise geográfica",
                "Classificação de riscos",
            ],
        }

    @app.post("/analyze/")
    async def analyze_logs(
        firewall_log: Optional[UploadFile] = File(None),
        auth_log: Optional[UploadFile] = File(None),
    ) -> JSONResponse:
        """
        Análise de logs de segurança.

        Aceita uploads de arquivos CSV ou JSON para análise.
        """
        if not firewall_log and not auth_log:
            raise HTTPException(
                status_code=400, detail="Pelo menos um arquivo deve ser enviado"
            )

        try:
            service = AnalysisService()
            results = service.analyze_files(firewall_log, auth_log)
            return JSONResponse(content=results, status_code=200)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            raise HTTPException(
                status_code=500, detail=f"Erro interno: {str(e)}"
            ) from e

else:
    app = None


# Ponto de entrada principal
if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        try:
            import uvicorn

            uvicorn.run(
                "log_analyzer.api:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="info",
            )
        except ImportError:
            logger.error("Uvicorn não disponível")
    else:
        logger.error("FastAPI não disponível - não é possível executar API")
