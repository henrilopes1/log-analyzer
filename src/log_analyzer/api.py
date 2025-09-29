"""
API REST para o Log Analyzer

Esta API fornece endpoints para análise de logs de segurança cibernética,
permitindo upload de arquivos de logs e retornando análises detalhadas
sobre ameaças detectadas, ataques de força bruta e varreduras de porta.
"""

import io
import json
import logging
from typing import Dict, List, Optional, Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .core import LogAnalyzer

# Configurar logging para não interferir com a saída da API
logging.basicConfig(level=logging.WARNING)

# Criar instância da aplicação FastAPI
app = FastAPI(
    title="Log Analyzer API",
    description="API REST para análise de logs de segurança cibernética",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


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


def _process_uploaded_file(file: UploadFile) -> pd.DataFrame:
    """
    Processa um arquivo enviado e converte para DataFrame.
    
    Args:
        file: Arquivo enviado via upload
        
    Returns:
        pd.DataFrame: Dados do arquivo como DataFrame
        
    Raises:
        HTTPException: Se o arquivo não puder ser processado
    """
    try:
        # Ler conteúdo do arquivo
        content = file.file.read()
        
        # Detectar tipo de arquivo pela extensão
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.lower().endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            df = pd.DataFrame(data)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de arquivo não suportado: {file.filename}"
            )
            
        return df
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar arquivo {file.filename}: {str(e)}"
        )


def _safe_analyze_method(analyzer: LogAnalyzer, method_name: str, *args, **kwargs) -> Any:
    """
    Executa um método de análise de forma segura, capturando erros.
    
    Args:
        analyzer: Instância do LogAnalyzer
        method_name: Nome do método a ser executado
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        Any: Resultado do método ou None se houver erro
    """
    try:
        method = getattr(analyzer, method_name)
        return method(*args, **kwargs)
    except Exception as e:
        logging.warning(f"Erro ao executar {method_name}: {str(e)}")
        return None


def _dataframe_to_dict(df: pd.DataFrame) -> List[Dict]:
    """
    Converte DataFrame para lista de dicionários para serialização JSON.
    
    Args:
        df: DataFrame a ser convertido
        
    Returns:
        List[Dict]: Lista de registros como dicionários
    """
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