#!/usr/bin/env python3
"""
Script para executar testes da API Log Analyzer

Este script facilita a execução de diferentes tipos de testes
da API com opções flexíveis de configuração.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def check_dependencies():
    """Verificar se as dependências necessárias estão instaladas."""
    required_packages = ["pytest", "requests"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependências faltando:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n💡 Instale com: pip install pytest requests")
        return False
    
    return True


def check_api_availability(url: str) -> bool:
    """Verificar se a API está rodando e acessível."""
    try:
        import requests
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def run_tests(args):
    """Executar testes baseado nos argumentos fornecidos."""
    if not check_dependencies():
        return 1
    
    # Verificar se a API está rodando
    if not check_api_availability(args.api_url):
        print(f"⚠️  API não está acessível em {args.api_url}")
        print("💡 Certifique-se de que a API está rodando antes de executar os testes")
        if not args.force:
            return 1
    
    # Configurar variáveis de ambiente
    env = os.environ.copy()
    env["API_BASE_URL"] = args.api_url
    
    # Construir comando pytest
    cmd = ["python", "-m", "pytest"]
    
    # Adicionar argumentos baseados nas opções
    if args.verbose:
        cmd.append("-v")
    
    if args.quiet:
        cmd.append("-q")
    
    if args.markers:
        for marker in args.markers:
            cmd.extend(["-m", marker])
    
    if args.keywords:
        for keyword in args.keywords:
            cmd.extend(["-k", keyword])
    
    if args.coverage:
        cmd.extend(["--cov=src/log_analyzer", "--cov-report=html", "--cov-report=term"])
    
    if args.parallel:
        cmd.extend(["-n", "auto"])
    
    if args.timeout:
        cmd.extend(["--timeout", str(args.timeout)])
    
    # Adicionar arquivos de teste específicos se fornecidos
    if args.test_files:
        cmd.extend(args.test_files)
    else:
        cmd.append("tests/")
    
    # Executar testes
    print(f"🚀 Executando testes da API Log Analyzer...")
    print(f"📍 URL da API: {args.api_url}")
    print(f"⚡ Comando: {' '.join(cmd)}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, env=env)
        end_time = time.time()
        
        print("=" * 60)
        print(f"⏱️  Tempo total: {end_time - start_time:.1f}s")
        
        if result.returncode == 0:
            print("✅ Todos os testes passaram!")
        else:
            print("❌ Alguns testes falharam")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário")
        return 130
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return 1


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Executar testes da API Log Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s                                    # Executar todos os testes
  %(prog)s -v                                 # Executar com saída verbosa
  %(prog)s -m integration                     # Executar apenas testes de integração
  %(prog)s -k "test_health"                   # Executar testes que contenham "test_health"
  %(prog)s --coverage                         # Executar com relatório de cobertura
  %(prog)s --parallel                         # Executar testes em paralelo
  %(prog)s tests/test_api.py::TestAPIHealth   # Executar uma classe específica
        """
    )
    
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="URL base da API (default: http://127.0.0.1:8000)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Executar com saída verbosa"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Executar com saída mínima"
    )
    
    parser.add_argument(
        "-m", "--markers",
        action="append",
        help="Executar apenas testes com marcadores específicos (ex: slow, integration)"
    )
    
    parser.add_argument(
        "-k", "--keywords",
        action="append",
        help="Executar apenas testes que contenham as palavras-chave"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Gerar relatório de cobertura de código"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Executar testes em paralelo (requer pytest-xdist)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout para testes em segundos (default: 300)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forçar execução mesmo se a API não estiver acessível"
    )
    
    parser.add_argument(
        "test_files",
        nargs="*",
        help="Arquivos ou padrões de teste específicos"
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.verbose and args.quiet:
        parser.error("--verbose e --quiet são mutuamente exclusivos")
    
    sys.exit(run_tests(args))


if __name__ == "__main__":
    main()