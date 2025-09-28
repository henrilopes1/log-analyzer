"""
Configuração pytest para o Log Analyzer
"""
import pytest
import sys
from pathlib import Path

# Configurações do pytest
pytest_plugins = []

def pytest_configure(config):
    """Configuração do pytest"""
    # Adicionar src ao path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

@pytest.fixture
def sample_data_path():
    """Fixture que retorna o caminho para dados de teste"""
    return Path(__file__).parent.parent / "samples"

@pytest.fixture
def exports_path():
    """Fixture que retorna o caminho para exports"""
    return Path(__file__).parent.parent / "exports"