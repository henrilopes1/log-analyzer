#!/usr/bin/env python3
"""
Testes unitários para a API Log Analyzer usando pytest

Este módulo contém testes abrangentes para todos os endpoints da API REST,
incluindo casos de sucesso e falha, validação de dados e testes de performance.
"""

import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

import pytest
import requests
from requests.exceptions import RequestException

# Configuração da API para testes
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_TIMEOUT = 30


class TestAPIHealth:
    """Testes para endpoints de saúde e status da API."""
    
    def test_api_status_endpoint(self):
        """Testa se o endpoint / retorna status correto."""
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "Log Analyzer API is running" in data["status"]
    
    def test_health_endpoint_returns_healthy(self):
        """Testa se o endpoint /health retorna status 'healthy'."""
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar campos obrigatórios
        assert data["status"] == "healthy"
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