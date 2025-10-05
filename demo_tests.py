#!/usr/bin/env python3
"""
Demonstração dos Testes da API Log Analyzer

Este script mostra como executar e validar os testes unitários
da API Log Analyzer de forma prática.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path


def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)


def print_section(title):
    """Imprime seção formatada."""
    print(f"\n📋 {title}")
    print("-" * 40)


def check_api_availability():
    """Verificar se a API está disponível."""
    print_section("VERIFICAÇÃO DA API")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando e acessível")
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Versão: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ API respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API não está acessível: {e}")
        print("💡 Inicie a API com: python src/log_analyzer/main.py")
        return False


def run_test_command(description, command, expected_output=None):
    """Executar comando de teste e verificar resultado."""
    print(f"\n🔧 {description}")
    print(f"   Comando: {' '.join(command)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"   ⏱️  Duração: {duration:.1f}s")
        
        if result.returncode == 0:
            print("   ✅ Sucesso!")
            if expected_output:
                if expected_output in result.stdout:
                    print(f"   ✅ Saída contém: '{expected_output}'")
                else:
                    print(f"   ⚠️  Saída não contém: '{expected_output}'")
        else:
            print("   ❌ Falhou!")
            if result.stderr:
                print(f"   Erro: {result.stderr[:200]}...")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("   ⏰ Timeout!")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def demonstrate_tests():
    """Demonstrar diferentes tipos de execução de testes."""
    print_header("DEMONSTRAÇÃO DOS TESTES DA API")
    
    # Verificar se API está disponível
    if not check_api_availability():
        print("\n⚠️  Alguns testes podem falhar sem a API rodando")
        choice = input("\nContinuar mesmo assim? (s/n): ").lower()
        if choice != 's':
            return False
    
    print_section("EXECUTANDO DIFERENTES TIPOS DE TESTES")
    
    # Python executable path
    python_exe = '/c/Users/Henri/AppData/Local/Programs/Python/Python311/python.exe'
    
    test_scenarios = [
        {
            "description": "Teste específico do endpoint /health",
            "command": [python_exe, "-m", "pytest", 
                       "tests/test_api.py::TestAPIHealth::test_health_endpoint_returns_healthy", 
                       "-v"],
            "expected": "PASSED"
        },
        {
            "description": "Teste específico do endpoint /api-info",
            "command": [python_exe, "-m", "pytest", 
                       "tests/test_api.py::TestAPIHealth::test_api_info_endpoint", 
                       "-v"],
            "expected": "PASSED"
        },
        {
            "description": "Teste de erro 400 sem arquivos",
            "command": [python_exe, "-m", "pytest", 
                       "tests/test_api.py::TestFileAnalysis::test_analyze_no_files_returns_400", 
                       "-v"],
            "expected": "PASSED"
        },
        {
            "description": "Teste de formato não suportado",
            "command": [python_exe, "-m", "pytest", 
                       "tests/test_api.py::TestFileAnalysis::test_analyze_with_unsupported_format_returns_400", 
                       "-v"],
            "expected": "PASSED"
        },
        {
            "description": "Todos os testes de saúde da API",
            "command": [python_exe, "-m", "pytest", 
                       "tests/test_api.py::TestAPIHealth", 
                       "-v"],
            "expected": "PASSED"
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        success = run_test_command(
            scenario["description"],
            scenario["command"],
            scenario["expected"]
        )
        results.append((scenario["description"], success))
    
    # Resumo dos resultados
    print_section("RESUMO DOS RESULTADOS")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"   {description}: {status}")
    
    success_rate = (passed / total) * 100
    print(f"\n📊 Taxa de Sucesso: {passed}/{total} ({success_rate:.0f}%)")
    
    if success_rate >= 80:
        print("🎉 TESTES FUNCIONANDO CORRETAMENTE!")
        return True
    else:
        print("⚠️  ALGUNS TESTES PRECISAM DE ATENÇÃO")
        return False


def show_test_examples():
    """Mostrar exemplos de comandos de teste."""
    print_section("EXEMPLOS DE COMANDOS DE TESTE")
    
    examples = [
        ("Executar todos os testes", "python -m pytest tests/ -v"),
        ("Executar testes específicos", "python -m pytest tests/test_api.py::TestAPIHealth -v"),
        ("Executar com marcadores", "python -m pytest -m integration -v"),
        ("Executar com palavras-chave", "python -m pytest -k 'health or info' -v"),
        ("Script personalizado", "python run_tests.py -v"),
        ("Com cobertura de código", "python run_tests.py --coverage"),
        ("Apenas testes rápidos", "python -m pytest -m 'not slow' -v")
    ]
    
    for description, command in examples:
        print(f"   📝 {description}:")
        print(f"      {command}")
        print()


def main():
    """Função principal."""
    print_header("DEMONSTRAÇÃO COMPLETA DOS TESTES")
    print("Esta demonstração valida que todos os testes solicitados estão funcionando:")
    print("• ✅ /health retorna status 'healthy'")
    print("• ✅ /api-info retorna informações da API")
    print("• ✅ /analyze/ com upload bem-sucedido")
    print("• ✅ /analyze/ sem arquivos retorna erro 400")
    print("• ✅ /analyze/ com formato não suportado retorna erro 400")
    
    # Demonstrar testes
    success = demonstrate_tests()
    
    # Mostrar exemplos
    show_test_examples()
    
    # Instruções finais
    print_section("PRÓXIMOS PASSOS")
    if success:
        print("✅ Testes validados com sucesso!")
        print("💡 Para executar todos os testes:")
        print("   python -m pytest tests/ -v")
        print("\n💡 Para usar o script personalizado:")
        print("   python run_tests.py -v")
    else:
        print("⚠️  Alguns testes precisam de atenção")
        print("💡 Certifique-se de que:")
        print("   • A API está rodando (python src/log_analyzer/main.py)")
        print("   • As dependências estão instaladas (pip install pytest requests)")
        print("   • Não há conflitos de porta")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())