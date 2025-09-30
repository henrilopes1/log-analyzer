"""
Aplicação FastAPI principal - refatorada e organizada
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import StatusEndpoints, AnalysisEndpoints
from .models import (
    AnalysisResponse, 
    APIInfo, 
    HealthResponse, 
    StatusResponse,
    ErrorResponse
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Log Analyzer API",
    description="API REST para análise de logs de segurança cibernética",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    responses={
        400: {"model": ErrorResponse, "description": "Erro de validação"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar endpoints de status
app.get(
    "/",
    response_model=StatusResponse,
    summary="Status da API",
    description="Retorna o status atual da API"
)(StatusEndpoints.get_status)

app.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificação de saúde",
    description="Verifica a saúde da API e retorna informações detalhadas"
)(StatusEndpoints.get_health)

app.get(
    "/api-info",
    response_model=APIInfo,
    summary="Informações da API",
    description="Retorna informações detalhadas sobre a API e seus recursos"
)(StatusEndpoints.get_api_info)

# Registrar endpoints de análise
app.post(
    "/analyze/",
    response_model=None,  # Usamos JSONResponse diretamente
    summary="Análise de logs",
    description="""
    Endpoint principal para análise de logs de segurança.
    
    Aceita uploads de arquivos de logs de firewall e/ou autenticação em formato CSV ou JSON.
    Executa análises abrangentes incluindo:
    - Detecção de ataques de força bruta
    - Identificação de varreduras de porta
    - Análise geográfica de IPs suspeitos
    - Classificação de riscos
    - Geração de estatísticas detalhadas
    
    Pelo menos um arquivo deve ser enviado.
    """,
    responses={
        200: {
            "description": "Análise concluída com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "summary": {
                            "files_processed": 2,
                            "total_events": 1000,
                            "analysis_completed": True,
                            "processing_time_seconds": 2.5
                        },
                        "brute_force_attacks": [],
                        "top_suspicious_ips": [],
                        "alerts": {
                            "high_risk": [],
                            "medium_risk": [],
                            "low_risk": []
                        }
                    }
                }
            }
        },
        400: {"description": "Erro de validação ou formato de arquivo"},
        413: {"description": "Arquivo muito grande"},
        500: {"description": "Erro interno do servidor"}
    }
)(AnalysisEndpoints.analyze_logs)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Event handler para inicialização da aplicação."""
    logger.info("🚀 Log Analyzer API iniciada com sucesso")
    logger.info("📍 Documentação disponível em /docs e /redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """Event handler para encerramento da aplicação."""
    logger.info("👋 Log Analyzer API finalizada")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler para endpoints não encontrados."""
    return ErrorResponse(
        error="Endpoint não encontrado",
        detail=f"O endpoint {request.url.path} não existe",
        code=404,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler para erros internos."""
    logger.error(f"Erro interno: {exc}")
    return ErrorResponse(
        error="Erro interno do servidor",
        detail="Ocorreu um erro inesperado. Tente novamente mais tarde.",
        code=500,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "log_analyzer.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )