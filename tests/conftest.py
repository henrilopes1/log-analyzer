"""
Configurações do pytest para testes da API Log Analyzer

Este arquivo contém configurações globais e fixtures compartilhadas
para todos os testes da suíte de testes.
"""

import os
import pytest
import requests
from requests.exceptions import RequestException


def pytest_configure(config):
    """Configuração executada antes de todos os testes."""
    # Adicionar marcadores customizados
    config.addinivalue_line(
        "markers", "slow: marca testes que são lentos para executar"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )


@pytest.fixture(scope="session")
def api_base_url():
    """Fixture que retorna a URL base da API."""
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def api_client(api_base_url):
    """Fixture que retorna um cliente HTTP configurado para a API."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "pytest-log-analyzer/1.0.0",
        "Accept": "application/json"
    })
    
    # Verificar se a API está acessível
    try:
        response = session.get(f"{api_base_url}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("API não está disponível para testes")
    except RequestException:
        pytest.skip("API não está acessível para testes")
    
    return session


@pytest.fixture
def sample_firewall_data():
    """Fixture com dados de firewall para testes."""
    return """timestamp,source_ip,destination_ip,port,protocol,action
2024-01-01 10:00:01,192.168.1.100,10.0.0.1,80,TCP,ALLOW
2024-01-01 10:00:02,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:03,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:04,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:05,192.168.1.200,10.0.0.1,443,TCP,ALLOW
2024-01-01 10:00:06,10.0.0.100,8.8.8.8,53,UDP,ALLOW"""


@pytest.fixture
def sample_auth_data():
    """Fixture com dados de autenticação para testes."""
    return """timestamp,username,source_ip,event_type,success
2024-01-01 10:01:01,admin,192.168.1.50,login,true
2024-01-01 10:01:05,admin,203.0.113.5,login,false
2024-01-01 10:01:10,admin,203.0.113.5,login,false
2024-01-01 10:01:15,admin,203.0.113.5,login,false
2024-01-01 10:01:20,user1,192.168.1.100,login,true
2024-01-01 10:01:25,user2,10.0.0.50,login,true"""


def pytest_collection_modifyitems(config, items):
    """Modifica itens coletados para adicionar marcadores automáticos."""
    for item in items:
        # Marcar testes que fazem upload de arquivo como lentos
        if "upload" in item.name.lower() or "large_file" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Marcar testes de API como integração
        if item.cls and "API" in item.cls.__name__:
            item.add_marker(pytest.mark.integration)