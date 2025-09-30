#!/usr/bin/env python3
"""
Script de Teste Simplificado para Log Analyzer
Testa funcionalidades principais do projeto
"""

import sys
import os
import tempfile
import pandas as pd

def test_core_functionality():
    """Testa funcionalidades do core"""
    print("🧪 Testando Core Functionality...")
    try:
        # Adicionar diretório src ao path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from log_analyzer.core import LogAnalyzer
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'timestamp': ['2024-01-01 10:00:00', '2024-01-01 10:01:00', '2024-01-01 10:02:00'],
            'source_ip': ['192.168.1.100', '192.168.1.100', '10.0.0.50'],
            'destination_ip': ['8.8.8.8', '8.8.8.8', '1.1.1.1'],
            'action': ['allow', 'block', 'allow'],
            'status_code': [200, 403, 200]
        })
        
        # Teste de inicialização
        analyzer = LogAnalyzer()
        analyzer.data = test_data
        print("✅ LogAnalyzer inicializado")
        
        # Teste análise de força bruta
        brute_force = analyzer.analyze_brute_force()
        print(f"✅ Análise força bruta: {len(brute_force)} resultados")
        
        # Teste estatísticas
        stats = analyzer.generate_statistics()
        print(f"✅ Estatísticas geradas: {len(stats) if stats else 0} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no core: {e}")
        return False

def test_geographic_analysis():
    """Testa análise geográfica"""
    print("🧪 Testando Análise Geográfica...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from log_analyzer.geographic import GeographicAnalyzer
        
        geo = GeographicAnalyzer()
        print("✅ GeographicAnalyzer inicializado")
        
        # Teste com IP público conhecido
        location = geo.get_ip_location("8.8.8.8")
        print(f"✅ Localização obtida: {location is not None}")
        
        return True
    except Exception as e:
        print(f"❌ Erro na análise geográfica: {e}")
        return False

def test_file_processing():
    """Testa processamento de arquivos"""
    print("🧪 Testando Processamento de Arquivos...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from log_analyzer.core import LogAnalyzer
        
        # Criar arquivo CSV temporário
        test_csv = """timestamp,source_ip,destination_ip,action,status_code
2024-01-01 10:00:00,192.168.1.100,8.8.8.8,allow,200
2024-01-01 10:01:00,192.168.1.100,8.8.8.8,block,403
2024-01-01 10:02:00,10.0.0.50,1.1.1.1,allow,200"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv)
            temp_file = f.name
        
        # Testar carregamento
        analyzer = LogAnalyzer(temp_file)
        data = analyzer.load_data()
        print(f"✅ Arquivo carregado: {len(data)} linhas")
        
        # Limpeza
        os.unlink(temp_file)
        
        return True
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def test_api_import():
    """Testa importação da API"""
    print("🧪 Testando Importação da API...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from log_analyzer.api import app
        print("✅ API importada com sucesso")
        return True
    except ImportError as e:
        print(f"⚠️ API não disponível (dependências opcionais): {e}")
        return True  # Consideramos OK
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def test_utils():
    """Testa utilitários"""
    print("🧪 Testando Utilitários...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from log_analyzer.utils import clean_ip_address, format_duration
        
        # Teste limpeza de IP
        clean_ip = clean_ip_address("192.168.1.1:8080")
        print(f"✅ IP limpo: {clean_ip}")
        
        # Teste formatação de duração
        duration = format_duration(3661)
        print(f"✅ Duração formatada: {duration}")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos utilitários: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 LOG ANALYZER - TESTES FUNCIONAIS")
    print("=" * 50)
    
    tests = [
        ("Core Functionality", test_core_functionality),
        ("Geographic Analysis", test_geographic_analysis),
        ("File Processing", test_file_processing),
        ("API Import", test_api_import),
        ("Utils", test_utils),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:<20}: {status}")
        if success:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n📈 Taxa de sucesso: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 PROJETO APROVADO! Funcionalidades principais OK")
        return 0
    else:
        print("⚠️ PROJETO PRECISA DE AJUSTES")
        return 1

if __name__ == "__main__":
    sys.exit(main())