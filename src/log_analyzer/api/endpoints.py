"""
Endpoints da API organizados por funcionalidade
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..core import LogAnalyzer
from .dependencies import get_analyzer, get_start_time
from .models import (
    AnalysisResponse, 
    APIInfo, 
    HealthResponse, 
    StatusResponse,
    SummaryData,
    AlertData,
    SuspiciousIP
)
from .utils import FileProcessor, AnalysisProcessor

logger = logging.getLogger(__name__)


class StatusEndpoints:
    """Endpoints relacionados ao status da API."""
    
    @staticmethod
    def get_status() -> StatusResponse:
        """Endpoint de status básico da API."""
        return StatusResponse(
            status="Log Analyzer API is running",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    @staticmethod
    def get_health() -> HealthResponse:
        """Endpoint de verificação de saúde da API."""
        start_time = get_start_time()
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - start_time).total_seconds()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            service="log-analyzer-api",
            timestamp=current_time.isoformat(),
            uptime_seconds=uptime
        )
    
    @staticmethod
    def get_api_info() -> APIInfo:
        """Informações sobre a API e seus endpoints."""
        return APIInfo(
            name="Log Analyzer API",
            version="1.0.0",
            description="API REST para análise de logs de segurança cibernética",
            endpoints={
                "/": "Status da API",
                "/health": "Verificação de saúde",
                "/analyze/": "Análise de logs (POST com upload de arquivos)",
                "/api-info": "Informações sobre a API",
                "/docs": "Documentação interativa (Swagger)",
                "/redoc": "Documentação alternativa (ReDoc)"
            },
            supported_formats=["CSV", "JSON"],
            supported_log_types=["firewall", "authentication"],
            features=[
                "Detecção de ataques de força bruta",
                "Análise de varreduras de porta",
                "Análise geográfica de IPs",
                "Classificação de riscos",
                "Estatísticas detalhadas",
                "Identificação de IPs suspeitos"
            ]
        )


class AnalysisEndpoints:
    """Endpoints relacionados à análise de logs."""
    
    @staticmethod
    def analyze_logs(
        firewall_log: Optional[UploadFile] = File(None),
        auth_log: Optional[UploadFile] = File(None),
        analyzer: LogAnalyzer = Depends(get_analyzer)
    ) -> JSONResponse:
        """
        Endpoint principal para análise de logs de segurança.
        
        Args:
            firewall_log: Arquivo de log do firewall (CSV ou JSON) - opcional
            auth_log: Arquivo de log de autenticação (CSV ou JSON) - opcional
            analyzer: Instância do LogAnalyzer
            
        Returns:
            JSONResponse: Resultados da análise em formato JSON
            
        Raises:
            HTTPException: Se nenhum arquivo for enviado ou erro no processamento
        """
        start_time = time.time()
        
        # Validar entrada
        if not firewall_log and not auth_log:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um arquivo de log deve ser enviado (firewall_log ou auth_log)"
            )
        
        try:
            # Processar arquivos
            processed_data = AnalysisEndpoints._process_uploaded_files(
                firewall_log, auth_log, analyzer
            )
            
            # Executar análises
            analysis_results = AnalysisEndpoints._execute_analysis(
                analyzer, processed_data
            )
            
            # Calcular tempo de processamento
            processing_time = time.time() - start_time
            analysis_results.summary.processing_time_seconds = processing_time
            
            # Adicionar metadados
            analysis_results.metadata.update({
                "api_version": "1.0.0",
                "analyzer_version": getattr(analyzer, 'version', '1.0.0'),
                "files_uploaded": [
                    f.filename for f in [firewall_log, auth_log] if f is not None
                ],
                "processing_time_seconds": processing_time,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return JSONResponse(
                content=analysis_results.model_dump(),
                status_code=200
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro interno durante análise: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno durante a análise: {str(e)}"
            ) from e
    
    @staticmethod
    def _process_uploaded_files(
        firewall_log: Optional[UploadFile], 
        auth_log: Optional[UploadFile],
        analyzer: LogAnalyzer
    ) -> Dict[str, int]:
        """
        Processa arquivos enviados e prepara dados para análise.
        
        Returns:
            Dict contendo informações sobre o processamento
        """
        files_processed = 0
        total_events = 0
        
        # Processar firewall log
        if firewall_log:
            try:
                firewall_df = FileProcessor.process_file(firewall_log)
                analyzer.data = firewall_df
                files_processed += 1
                total_events += len(firewall_df)
                logger.info(f"Processado firewall log: {len(firewall_df)} eventos")
                
            except Exception as e:
                logger.error(f"Erro ao processar firewall log: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro ao processar firewall log: {str(e)}"
                ) from e
        
        # Processar auth log
        if auth_log:
            try:
                auth_df = FileProcessor.process_file(auth_log)
                
                if analyzer.data is not None:
                    # Combinar com dados existentes
                    import pandas as pd
                    analyzer.data = pd.concat(
                        [analyzer.data, auth_df], 
                        ignore_index=True, 
                        sort=False
                    )
                else:
                    analyzer.data = auth_df
                
                files_processed += 1
                total_events += len(auth_df)
                logger.info(f"Processado auth log: {len(auth_df)} eventos")
                
            except Exception as e:
                logger.error(f"Erro ao processar auth log: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro ao processar auth log: {str(e)}"
                ) from e
        
        return {
            "files_processed": files_processed,
            "total_events": total_events
        }
    
    @staticmethod
    def _execute_analysis(analyzer: LogAnalyzer, processed_data: Dict[str, int]) -> AnalysisResponse:
        """
        Executa análises nos dados processados.
        
        Args:
            analyzer: Instância do LogAnalyzer
            processed_data: Informações sobre dados processados
            
        Returns:
            AnalysisResponse: Resultados da análise
        """
        # Inicializar resposta
        response = AnalysisResponse(
            summary=SummaryData(
                files_processed=processed_data["files_processed"],
                total_events=processed_data["total_events"],
                analysis_completed=True
            )
        )
        
        if analyzer.data is None or analyzer.data.empty:
            return response
        
        # Análise de firewall
        firewall_results = AnalysisProcessor.safe_execute_analysis(
            analyzer, 'analyze_firewall_logs', analyzer.data
        )
        if firewall_results is not None:
            response.firewall_analysis = AnalysisProcessor.dataframe_to_records(firewall_results)
        
        # Análise de força bruta
        brute_force_results = AnalysisProcessor.safe_execute_analysis(
            analyzer, 'analyze_brute_force'
        )
        if brute_force_results is not None:
            response.brute_force_attacks = AnalysisProcessor.dataframe_to_records(brute_force_results)
        
        # Estatísticas
        stats = AnalysisProcessor.safe_execute_analysis(analyzer, 'generate_statistics')
        if stats:
            response.statistics = stats
        
        # IPs suspeitos
        suspicious_ips = AnalysisProcessor.extract_suspicious_ips(analyzer.data)
        response.top_suspicious_ips = [
            SuspiciousIP(**ip_data) for ip_data in suspicious_ips
        ]
        
        # Classificar alertas por risco
        response.alerts = AnalysisEndpoints._classify_alerts(suspicious_ips)
        
        # Análise geográfica (se disponível)
        try:
            geo_results = AnalysisEndpoints._perform_geographic_analysis(analyzer)
            response.geographic_analysis = geo_results
        except Exception as e:
            logger.warning(f"Análise geográfica falhou: {e}")
            response.geographic_analysis = []
        
        return response
    
    @staticmethod
    def _classify_alerts(suspicious_ips: List[Dict[str, Any]]) -> AlertData:
        """Classifica alertas por nível de risco."""
        alerts = AlertData()
        
        for ip_data in suspicious_ips:
            suspicious_ip = SuspiciousIP(**ip_data)
            
            if suspicious_ip.risk_level == "high":
                alerts.high_risk.append(suspicious_ip)
            elif suspicious_ip.risk_level == "medium":
                alerts.medium_risk.append(suspicious_ip)
            else:
                alerts.low_risk.append(suspicious_ip)
        
        return alerts
    
    @staticmethod
    def _perform_geographic_analysis(analyzer: LogAnalyzer) -> List[Dict[str, Any]]:
        """Executa análise geográfica se disponível."""
        try:
            from ..geographic import GeographicAnalyzer
            
            geo_analyzer = GeographicAnalyzer()
            
            # Extrair IPs únicos
            unique_ips = []
            if 'source_ip' in analyzer.data.columns:
                unique_ips.extend(analyzer.data['source_ip'].dropna().unique().tolist())
            
            if unique_ips:
                # Limitar a 10 IPs para evitar sobrecarga
                return geo_analyzer.analyze_ips(unique_ips[:10])
            
            return []
            
        except ImportError:
            logger.warning("GeographicAnalyzer não disponível")
            return []
        except Exception as e:
            logger.error(f"Erro na análise geográfica: {e}")
            return []