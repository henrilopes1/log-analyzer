#!/usr/bin/env python3
"""
Log Analyzer - Wrapper de compatibilidade

DEPRECATED: Este arquivo é mantido apenas para compatibilidade.
Use a nova estrutura modular:
    python -m src.log_analyzer --samples
    ou instale como pacote: pip install -e .
    e use: analyzer --samples

Este wrapper redireciona para a implementação modular.
"""

import sys
import warnings
from pathlib import Path

# Adicionar src ao path para importar o módulo
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from log_analyzer.main import main
    
    # Aviso de deprecação
    warnings.warn(
        "main.py é deprecated. Use 'python -m src.log_analyzer' ou instale com 'pip install -e .' e use 'analyzer'",
        DeprecationWarning,
        stacklevel=2
    )
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Erro ao importar módulo: {e}")
    print("💡 Certifique-se de que a estrutura modular está correta")
    sys.exit(1)