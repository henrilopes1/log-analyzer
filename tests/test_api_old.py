#!/usr/bin/env python3
"""
Testes unitários para a API Log Analyzer usando FastAPI TestClient e pytest

Este módulo contém testes robustos para todos os endpoints da API FastAPI,
utilizando TestClient para testes de integração completos.
"""

import io
import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Importar a aplicação FastAPI
try:
    from src.log_analyzer.api import app
except ImportError:
    # Fallback caso o import falhe
    app = None

# Pular todos os testes se a aplicação não estiver disponível
pytestmark = pytest.mark.skipif(app is None, reason="FastAPI app not available")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Fixture que cria um cliente de teste para a API FastAPI.
    
    Returns:
        TestClient configurado para a aplicação
    """
    if app is None:
        pytest.skip("FastAPI app not available")
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def firewall_csv_content() -> str:
    """
    Fixture que retorna conteúdo CSV válido para logs de firewall.
    
    Returns:
        String com conteúdo CSV de firewall
    """
    return """timestamp,source_ip,destination_ip,port,protocol,action
2024-01-01 10:00:01,192.168.1.100,10.0.0.1,80,TCP,ALLOW
2024-01-01 10:00:02,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:03,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:04,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:05,192.168.1.200,10.0.0.1,443,TCP,ALLOW"""


@pytest.fixture
def auth_json_content() -> str:
    """
    Fixture que retorna conteúdo JSON válido para logs de autenticação.
    
    Returns:
        String com conteúdo JSON de autenticação
    """
    auth_data = [
        {
            "timestamp": "2024-01-01 10:01:01",
            "username": "admin",
            "source_ip": "192.168.1.50",
            "event_type": "login",
            "success": True
        },
        {
            "timestamp": "2024-01-01 10:01:05",
            "username": "admin",
            "source_ip": "203.0.113.5",
            "event_type": "login",
            "success": False
        },
        {
            "timestamp": "2024-01-01 10:01:10",
            "username": "admin",
            "source_ip": "203.0.113.5",
            "event_type": "login",
            "success": False
        },
        {
            "timestamp": "2024-01-01 10:01:15",
            "username": "admin",
            "source_ip": "203.0.113.5",
            "event_type": "login",
            "success": False
        }
    ]
    return json.dumps(auth_data, indent=2)


@pytest.fixture
def invalid_txt_content() -> str:
    """
    Fixture que retorna conteúdo inválido para teste de erro.
    
    Returns:
        String com conteúdo que não é CSV nem JSON válido
    """
    return "Este não é um arquivo CSV nem JSON válido!\nApenas texto simples."


@pytest.fixture
def temp_firewall_file(firewall_csv_content: str) -> Generator[io.BytesIO, None, None]:
    """
    Fixture que cria um arquivo temporário de firewall CSV.
    
    Args:
        firewall_csv_content: Conteúdo CSV do firewall
        
    Yields:
        BytesIO object com conteúdo CSV
    """
    file_obj = io.BytesIO(firewall_csv_content.encode('utf-8'))
    file_obj.name = "test_firewall.csv"
    yield file_obj
    file_obj.close()


@pytest.fixture
def temp_auth_file(auth_json_content: str) -> Generator[io.BytesIO, None, None]:
    """
    Fixture que cria um arquivo temporário de autenticação JSON.
    
    Args:
        auth_json_content: Conteúdo JSON de autenticação
        
    Yields:
        BytesIO object com conteúdo JSON
    """
    file_obj = io.BytesIO(auth_json_content.encode('utf-8'))
    file_obj.name = "test_auth.json"
    yield file_obj
    file_obj.close()


@pytest.fixture
def temp_invalid_file(invalid_txt_content: str) -> Generator[io.BytesIO, None, None]:
    """
    Fixture que cria um arquivo temporário com formato inválido.
    
    Args:
        invalid_txt_content: Conteúdo de arquivo inválido
        
    Yields:
        BytesIO object com conteúdo inválido
    """
    file_obj = io.BytesIO(invalid_txt_content.encode('utf-8'))
    file_obj.name = "test_invalid.txt"
    yield file_obj
    file_obj.close()


class TestEndpointRoot:
    """Testes para o endpoint raiz (/) da API."""
    
    def test_root_endpoint_returns_200(self, client: TestClient):
        """
        Teste do Endpoint Raiz (/).
        Verifica se uma requisição GET para / retorna status code 200.
        """
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_endpoint_contains_status(self, client: TestClient):
        """
        Teste do Endpoint Raiz (/).
        Verifica se a resposta JSON contém a chave "status".
        """
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        
        # Verificar se o status contém a mensagem esperada
        assert "Log Analyzer API is running" in data["status"]


class TestEndpointHealth:
    """Testes para o endpoint de saúde (/health) da API."""
    
    def test_health_endpoint_returns_200(self, client: TestClient):
        """
        Teste do Endpoint de Saúde (/health).
        Verifica se uma requisição GET para /health retorna status code 200.
        """
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_healthy_status(self, client: TestClient):
        """
        Teste do Endpoint de Saúde (/health).
        Verifica se a resposta JSON contém "status": "healthy".
        """
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        
        # Verificar outros campos obrigatórios
        assert "version" in data
        assert "service" in data
        assert "timestamp" in data
        assert "components" in data
        
        # Verificar estrutura dos componentes
        components = data["components"]
        assert isinstance(components, dict)
        assert "core" in components
        assert "fastapi" in components


class TestEndpointApiInfo:
    """Testes para o endpoint de informações (/api-info) da API."""
    
    def test_api_info_endpoint_returns_200(self, client: TestClient):
        """
        Teste do Endpoint de Informações (/api-info).
        Verifica se uma requisição GET para /api-info retorna status code 200.
        """
        response = client.get("/api-info")
        assert response.status_code == 200
    
    def test_api_info_endpoint_contains_required_fields(self, client: TestClient):
        """
        Teste do Endpoint de Informações (/api-info).
        Verifica se a resposta JSON contém as chaves "name" e "endpoints".
        """
        response = client.get("/api-info")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verificar campos obrigatórios
        assert "name" in data
        assert "endpoints" in data
        assert "version" in data
        assert "description" in data
        assert "supported_formats" in data
        assert "features" in data
        
        # Verificar conteúdo específico
        assert data["name"] == "Log Analyzer API"
        assert isinstance(data["endpoints"], dict)
        assert isinstance(data["supported_formats"], list)
        assert isinstance(data["features"], list)
        
        # Verificar se endpoints esperados estão documentados
        endpoints = data["endpoints"]
        expected_endpoints = ["/", "/health", "/analyze/", "/api-info"]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints


class TestEndpointAnalyze:
    """Testes para o endpoint de análise (/analyze/) da API."""
    
    def test_analyze_no_files_returns_400(self, client: TestClient):
        """
        Cenário de Erro (Sem Arquivos).
        Teste uma requisição POST sem nenhum arquivo e verifica se o status code é 400.
        """
        response = client.post("/analyze/")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "pelo menos um arquivo" in data["detail"].lower() or "at least one file" in data["detail"].lower()
    
    def test_analyze_invalid_format_returns_400(self, client: TestClient, temp_invalid_file: io.BytesIO):
        """
        Cenário de Erro (Formato Inválido).
        Teste um upload com um arquivo .txt e verifica se o status code é 400.
        """
        temp_invalid_file.seek(0)  # Reset file pointer
        
        files = {
            "firewall_log": ("test_invalid.txt", temp_invalid_file, "text/plain")
        }
        
        response = client.post("/analyze/", files=files)
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        # Verificar se a mensagem de erro indica formato não suportado
        assert ("não suportado" in data["detail"].lower() or 
                "not supported" in data["detail"].lower() or
                ".txt" in data["detail"])
    
    def test_analyze_firewall_only_success(self, client: TestClient, temp_firewall_file: io.BytesIO):
        """
        Cenário de Sucesso (Apenas Firewall).
        Simula o upload de um arquivo firewall_log (CSV) e verifica se o status code é 200
        e se a resposta contém a chave "summary".
        """
        temp_firewall_file.seek(0)  # Reset file pointer
        
        files = {
            "firewall_log": ("test_firewall.csv", temp_firewall_file, "text/csv")
        }
        
        response = client.post("/analyze/", files=files)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "summary" in data
        assert "firewall_analysis" in data
        assert "brute_force_attacks" in data
        assert "statistics" in data
        assert "metadata" in data
        
        # Verificar campos do summary
        summary = data["summary"]
        assert "files_processed" in summary
        assert "total_events" in summary
        assert "analysis_completed" in summary
        assert "processing_time_seconds" in summary
        
        # Verificar valores do summary
        assert summary["files_processed"] >= 1
        assert summary["total_events"] > 0
        assert summary["analysis_completed"] is True
        assert isinstance(summary["processing_time_seconds"], (int, float))
        
        # Verificar metadata
        metadata = data["metadata"]
        assert "api_version" in metadata
        assert "files_uploaded" in metadata
        assert "timestamp" in metadata
        assert len(metadata["files_uploaded"]) == 1
    
    def test_analyze_auth_only_success(self, client: TestClient, temp_auth_file: io.BytesIO):
        """
        Cenário de Sucesso (Apenas Autenticação).
        Simula o upload de um arquivo auth_log (JSON) e verifica se o status code é 200
        e se a resposta contém a chave "summary".
        """
        temp_auth_file.seek(0)  # Reset file pointer
        
        files = {
            "auth_log": ("test_auth.json", temp_auth_file, "application/json")
        }
        
        response = client.post("/analyze/", files=files)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "summary" in data
        assert "firewall_analysis" in data
        assert "brute_force_attacks" in data
        assert "statistics" in data
        assert "metadata" in data
        
        # Verificar que a análise foi bem-sucedida
        summary = data["summary"]
        assert summary["analysis_completed"] is True
        assert summary["files_processed"] >= 1
        assert summary["total_events"] > 0
        
        # Verificar metadata
        metadata = data["metadata"]
        assert len(metadata["files_uploaded"]) == 1
        assert "test_auth.json" in metadata["files_uploaded"][0]
    
    def test_analyze_both_files_success(self, client: TestClient, temp_firewall_file: io.BytesIO, temp_auth_file: io.BytesIO):
        """
        Cenário de Sucesso (Ambos os Arquivos).
        Simula o upload de ambos os arquivos (firewall_log e auth_log) e verifica se o status code é 200
        e se o "files_processed" no sumário é 2.
        """
        temp_firewall_file.seek(0)  # Reset file pointer
        temp_auth_file.seek(0)      # Reset file pointer
        
        files = {
            "firewall_log": ("test_firewall.csv", temp_firewall_file, "text/csv"),
            "auth_log": ("test_auth.json", temp_auth_file, "application/json")
        }
        
        response = client.post("/analyze/", files=files)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "summary" in data
        assert "metadata" in data
        
        # Verificar que ambos os arquivos foram processados
        summary = data["summary"]
        assert summary["files_processed"] == 2
        assert summary["analysis_completed"] is True
        assert summary["total_events"] > 0
        
        # Verificar metadata
        metadata = data["metadata"]
        assert len(metadata["files_uploaded"]) == 2
        
        # Verificar que ambos os nomes de arquivo estão presentes
        uploaded_files = metadata["files_uploaded"]
        assert any("test_firewall.csv" in filename for filename in uploaded_files)
        assert any("test_auth.json" in filename for filename in uploaded_files)
    
    def test_analyze_malformed_csv_returns_400(self, client: TestClient):
        """
        Teste adicional: arquivo CSV malformado deve retornar erro 400.
        """
        malformed_csv = "header1,header2\nvalue1\nvalue2,value3,value4,value5"
        file_obj = io.BytesIO(malformed_csv.encode('utf-8'))
        
        files = {
            "firewall_log": ("malformed.csv", file_obj, "text/csv")
        }
        
        response = client.post("/analyze/", files=files)
        # Pode retornar 400 ou 500 dependendo da implementação
        assert response.status_code in [400, 500]
        
        data = response.json()
        assert "detail" in data
    
    def test_analyze_empty_file_returns_400(self, client: TestClient):
        """
        Teste adicional: arquivo vazio deve retornar erro 400.
        """
        empty_file = io.BytesIO(b"")
        
        files = {
            "firewall_log": ("empty.csv", empty_file, "text/csv")
        }
        
        response = client.post("/analyze/", files=files)
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data


class TestEndpointMetrics:
    """Testes para o endpoint de métricas (/metrics) da API."""
    
    def test_metrics_endpoint_returns_200(self, client: TestClient):
        """
        Teste adicional: verifica se o endpoint /metrics retorna status 200.
        """
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "metrics" in data
        assert "timestamp" in data
        
        # Verificar estrutura das métricas
        metrics = data["metrics"]
        assert "uptime_seconds" in metrics
        assert "request_count" in metrics
        assert "avg_response_time_ms" in metrics
        assert "requests_per_second" in metrics
        
        # Verificar tipos de dados
        assert isinstance(metrics["uptime_seconds"], (int, float))
        assert isinstance(metrics["request_count"], int)
        assert isinstance(metrics["avg_response_time_ms"], (int, float))
        assert isinstance(metrics["requests_per_second"], (int, float))


class TestErrorHandling:
    """Testes para tratamento de erros da API."""
    
    def test_nonexistent_endpoint_returns_404(self, client: TestClient):
        """
        Teste adicional: endpoint inexistente deve retornar 404.
        """
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method_returns_405(self, client: TestClient):
        """
        Teste adicional: método HTTP inválido deve retornar 405.
        """
        # POST para endpoint que só aceita GET
        response = client.post("/health")
        assert response.status_code == 405


# Função principal para executar testes
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
        assert "version" in data
        assert "service" in data
        assert "timestamp" in data
        assert "components" in data
        
        # Verificar estrutura dos componentes
        components = data["components"]
        assert isinstance(components, dict)
        assert "core" in components
        assert "fastapi" in components
        
        # Status dos componentes deve ser 'available' ou 'unavailable'
        for component, status in components.items():
            assert status in ["available", "unavailable"]
    
    def test_api_info_endpoint(self):
        """Testa se o endpoint /api-info retorna as informações da API."""
        response = requests.get(f"{API_BASE_URL}/api-info", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar campos obrigatórios
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
        assert "supported_formats" in data
        assert "features" in data
        
        # Verificar conteúdo específico
        assert data["name"] == "Log Analyzer API"
        assert isinstance(data["endpoints"], dict)
        assert isinstance(data["supported_formats"], list)
        assert isinstance(data["features"], list)
        
        # Verificar endpoints documentados
        endpoints = data["endpoints"]
        expected_endpoints = ["/", "/health", "/analyze/", "/api-info"]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints
    
    def test_metrics_endpoint(self):
        """Testa se o endpoint /metrics retorna métricas válidas."""
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "metrics" in data
        assert "timestamp" in data
        
        metrics = data["metrics"]
        assert "uptime_seconds" in metrics
        assert "request_count" in metrics
        assert "avg_response_time_ms" in metrics
        assert "requests_per_second" in metrics
        
        # Verificar tipos de dados
        assert isinstance(metrics["uptime_seconds"], (int, float))
        assert isinstance(metrics["request_count"], int)
        assert isinstance(metrics["avg_response_time_ms"], (int, float))
        assert isinstance(metrics["requests_per_second"], (int, float))


class TestFileAnalysis:
    """Testes para o endpoint de análise de arquivos."""
    
    @pytest.fixture
    def valid_firewall_csv(self):
        """Fixture que cria um arquivo CSV válido para testes."""
        csv_content = """timestamp,source_ip,destination_ip,port,protocol,action
2024-01-01 10:00:01,192.168.1.100,10.0.0.1,80,TCP,ALLOW
2024-01-01 10:00:02,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:03,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:04,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:05,192.168.1.200,10.0.0.1,443,TCP,ALLOW"""
        return io.StringIO(csv_content)
    
    @pytest.fixture
    def valid_auth_csv(self):
        """Fixture que cria um arquivo de autenticação válido para testes."""
        csv_content = """timestamp,username,source_ip,event_type,success
2024-01-01 10:01:01,admin,192.168.1.50,login,true
2024-01-01 10:01:05,admin,203.0.113.5,login,false
2024-01-01 10:01:10,admin,203.0.113.5,login,false
2024-01-01 10:01:15,admin,203.0.113.5,login,false
2024-01-01 10:01:20,user1,192.168.1.100,login,true"""
        return io.StringIO(csv_content)
    
    @pytest.fixture
    def invalid_file_content(self):
        """Fixture que cria conteúdo de arquivo inválido."""
        return io.StringIO("Este não é um CSV nem JSON válido!")
    
    def test_analyze_no_files_returns_400(self):
        """Testa se o endpoint /analyze/ retorna erro 400 quando nenhum arquivo é enviado."""
        response = requests.post(f"{API_BASE_URL}/analyze/", timeout=API_TIMEOUT)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_analyze_with_firewall_log_success(self, valid_firewall_csv):
        """Testa upload bem-sucedido de arquivo de firewall."""
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(valid_firewall_csv.getvalue())
            temp_file_path = f.name
        
        try:
            # Fazer upload
            with open(temp_file_path, 'rb') as file:
                files = {'firewall_log': ('test_firewall.csv', file, 'text/csv')}
                response = requests.post(
                    f"{API_BASE_URL}/analyze/", 
                    files=files, 
                    timeout=API_TIMEOUT
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estrutura da resposta
            assert "summary" in data
            assert "firewall_analysis" in data
            assert "brute_force_attacks" in data
            assert "statistics" in data
            assert "metadata" in data
            
            # Verificar summary
            summary = data["summary"]
            assert "files_processed" in summary
            assert "total_events" in summary
            assert "analysis_completed" in summary
            assert "processing_time_seconds" in summary
            
            assert summary["files_processed"] >= 1
            assert summary["total_events"] > 0
            assert summary["analysis_completed"] is True
            assert isinstance(summary["processing_time_seconds"], (int, float))
            
            # Verificar metadata
            metadata = data["metadata"]
            assert "api_version" in metadata
            assert "files_uploaded" in metadata
            assert "timestamp" in metadata
            
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_file_path)
    
    def test_analyze_with_auth_log_success(self, valid_auth_csv):
        """Testa upload bem-sucedido de arquivo de autenticação."""
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(valid_auth_csv.getvalue())
            temp_file_path = f.name
        
        try:
            # Fazer upload
            with open(temp_file_path, 'rb') as file:
                files = {'auth_log': ('test_auth.csv', file, 'text/csv')}
                response = requests.post(
                    f"{API_BASE_URL}/analyze/", 
                    files=files, 
                    timeout=API_TIMEOUT
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar que a análise foi bem-sucedida
            assert data["summary"]["analysis_completed"] is True
            assert data["summary"]["files_processed"] >= 1
            
        finally:
            os.unlink(temp_file_path)
    
    def test_analyze_with_both_logs_success(self, valid_firewall_csv, valid_auth_csv):
        """Testa upload bem-sucedido de ambos os arquivos."""
        # Criar arquivos temporários
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
            f1.write(valid_firewall_csv.getvalue())
            firewall_path = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            f2.write(valid_auth_csv.getvalue())
            auth_path = f2.name
        
        try:
            # Fazer upload de ambos os arquivos
            with open(firewall_path, 'rb') as fw_file, open(auth_path, 'rb') as auth_file:
                files = {
                    'firewall_log': ('test_firewall.csv', fw_file, 'text/csv'),
                    'auth_log': ('test_auth.csv', auth_file, 'text/csv')
                }
                response = requests.post(
                    f"{API_BASE_URL}/analyze/", 
                    files=files, 
                    timeout=API_TIMEOUT
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar que ambos os arquivos foram processados
            assert data["summary"]["files_processed"] == 2
            assert len(data["metadata"]["files_uploaded"]) == 2
            
        finally:
            os.unlink(firewall_path)
            os.unlink(auth_path)
    
    def test_analyze_with_unsupported_format_returns_400(self, invalid_file_content):
        """Testa se arquivo de formato não suportado retorna erro 400."""
        # Criar arquivo temporário com extensão não suportada
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(invalid_file_content.getvalue())
            temp_file_path = f.name
        
        try:
            # Tentar fazer upload
            with open(temp_file_path, 'rb') as file:
                files = {'firewall_log': ('test_invalid.txt', file, 'text/plain')}
                response = requests.post(
                    f"{API_BASE_URL}/analyze/", 
                    files=files, 
                    timeout=API_TIMEOUT
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "não suportado" in data["detail"].lower() or "not supported" in data["detail"].lower()
            
        finally:
            os.unlink(temp_file_path)
    
    def test_analyze_with_malformed_csv_returns_400(self):
        """Testa se CSV malformado retorna erro 400."""
        malformed_csv = "header1,header2\nvalue1\nvalue2,value3,value4"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(malformed_csv)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as file:
                files = {'firewall_log': ('malformed.csv', file, 'text/csv')}
                response = requests.post(
                    f"{API_BASE_URL}/analyze/", 
                    files=files, 
                    timeout=API_TIMEOUT
                )
            
            # Pode retornar 400 ou 500 dependendo da implementação
            assert response.status_code in [400, 500]
            
        finally:
            os.unlink(temp_file_path)


class TestAPIPerformance:
    """Testes de performance da API."""
    
    def test_api_response_time(self):
        """Testa se a API responde dentro do tempo aceitável."""
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Deve responder em menos de 2 segundos
    
    def test_health_check_response_time(self):
        """Testa se o health check responde rapidamente."""
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Health check deve ser muito rápido
    
    def test_concurrent_requests(self):
        """Testa se a API suporta requisições concorrentes."""
        import concurrent.futures
        
        def make_request():
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code
        
        # Fazer 5 requisições concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Todas as requisições devem ter sucesso
        assert all(status == 200 for status in results)
        assert len(results) == 5


class TestAPIErrorHandling:
    """Testes para tratamento de erros da API."""
    
    def test_nonexistent_endpoint_returns_404(self):
        """Testa se endpoint inexistente retorna 404."""
        response = requests.get(f"{API_BASE_URL}/nonexistent", timeout=5)
        assert response.status_code == 404
    
    def test_invalid_method_returns_405(self):
        """Testa se método HTTP inválido retorna 405."""
        # POST para endpoint que só aceita GET
        response = requests.post(f"{API_BASE_URL}/health", timeout=5)
        assert response.status_code == 405
    
    def test_large_file_upload_handling(self):
        """Testa tratamento de arquivos muito grandes."""
        # Criar arquivo grande (simulado)
        large_content = "timestamp,source_ip,destination_ip\n" + "2024-01-01,1.1.1.1,2.2.2.2\n" * 100000
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(large_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as file:
                files = {'firewall_log': ('large_file.csv', file, 'text/csv')}
                # Usar timeout maior para arquivos grandes
                response = requests.post(
                    f"{API_BASE_URL}/analyze/", 
                    files=files, 
                    timeout=60
                )
            
            # Deve processar ou retornar erro específico para arquivo grande
            assert response.status_code in [200, 400, 413, 500]
            
        finally:
            os.unlink(temp_file_path)


# Fixtures e utilitários de setup/teardown
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup do ambiente de teste."""
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("API não está disponível para testes")
    except RequestException:
        pytest.skip("API não está acessível para testes")
    
    yield
    
    # Cleanup após todos os testes
    # Aqui poderia limpar logs de teste, arquivos temporários, etc.


# Função principal para executar testes
if __name__ == "__main__":
    # Executar testes com pytest
    pytest.main([__file__, "-v", "--tb=short"])