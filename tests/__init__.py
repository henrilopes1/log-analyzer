"""
Configuração de testes para o Log Analyzer
"""

import sys
from pathlib import Path

import pytest

# Adicionar src ao path para importar os módulos
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
