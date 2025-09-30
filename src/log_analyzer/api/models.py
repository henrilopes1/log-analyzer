"""
Modelos Pydantic para a API
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FileUploadInfo(BaseModel):
    """Informações sobre arquivo enviado"""
    
    filename: str = Field(..., description="Nome do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    content_type: str = Field(..., description="Tipo MIME do arquivo")


class AnalysisRequest(BaseModel):
    """Modelo de requisição para análise"""
    
    firewall_log: Optional[FileUploadInfo] = Field(None, description="Arquivo de log de firewall")
    auth_log: Optional[FileUploadInfo] = Field(None, description="Arquivo de log de autenticação")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Opções de análise")


class SummaryData(BaseModel):
    """Resumo da análise"""
    
    files_processed: int = Field(..., description="Número de arquivos processados")
    total_events: int = Field(..., description="Total de eventos analisados")
    analysis_completed: bool = Field(..., description="Status da análise")
    processing_time_seconds: Optional[float] = Field(None, description="Tempo de processamento")


class SuspiciousIP(BaseModel):
    """IP suspeito identificado"""
    
    ip: str = Field(..., description="Endereço IP")
    occurrences: int = Field(..., description="Número de ocorrências")
    risk_level: Optional[str] = Field(None, description="Nível de risco")


class GeographicInfo(BaseModel):
    """Informações geográficas de um IP"""
    
    ip: str = Field(..., description="Endereço IP")
    country: Optional[str] = Field(None, description="País")
    region: Optional[str] = Field(None, description="Região/Estado")
    city: Optional[str] = Field(None, description="Cidade")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")


class AlertData(BaseModel):
    """Dados de alerta por nível de risco"""
    
    high_risk: List[SuspiciousIP] = Field(default_factory=list, description="Alertas de alto risco")
    medium_risk: List[SuspiciousIP] = Field(default_factory=list, description="Alertas de médio risco")
    low_risk: List[SuspiciousIP] = Field(default_factory=list, description="Alertas de baixo risco")


class AnalysisResponse(BaseModel):
    """Modelo de resposta da análise"""
    
    summary: SummaryData = Field(..., description="Resumo da análise")
    firewall_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Análise do firewall")
    brute_force_attacks: List[Dict[str, Any]] = Field(default_factory=list, description="Ataques de força bruta")
    authentication_failures: List[Dict[str, Any]] = Field(default_factory=list, description="Falhas de autenticação")
    geographic_analysis: List[GeographicInfo] = Field(default_factory=list, description="Análise geográfica")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Estatísticas gerais")
    top_suspicious_ips: List[SuspiciousIP] = Field(default_factory=list, description="IPs mais suspeitos")
    alerts: AlertData = Field(default_factory=AlertData, description="Alertas por nível de risco")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados da análise")


class APIInfo(BaseModel):
    """Informações sobre a API"""
    
    name: str = Field(..., description="Nome da API")
    version: str = Field(..., description="Versão da API")
    description: str = Field(..., description="Descrição da API")
    endpoints: Dict[str, str] = Field(..., description="Endpoints disponíveis")
    supported_formats: List[str] = Field(..., description="Formatos de arquivo suportados")
    supported_log_types: List[str] = Field(..., description="Tipos de log suportados")
    features: List[str] = Field(..., description="Funcionalidades disponíveis")


class HealthResponse(BaseModel):
    """Resposta do health check"""
    
    status: str = Field(..., description="Status da aplicação")
    version: str = Field(..., description="Versão da aplicação")
    service: str = Field(..., description="Nome do serviço")
    timestamp: str = Field(..., description="Timestamp da verificação")
    uptime_seconds: Optional[float] = Field(None, description="Tempo de atividade em segundos")


class StatusResponse(BaseModel):
    """Resposta do status básico"""
    
    status: str = Field(..., description="Status da API")
    timestamp: str = Field(..., description="Timestamp da resposta")


class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
    code: Optional[int] = Field(None, description="Código do erro")
    timestamp: str = Field(..., description="Timestamp do erro")