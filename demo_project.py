#!/usr/bin/env python3
"""
Demonstração Completa do Log Analyzer
Mostra todas as funcionalidades do projeto em ação
"""

import sys
import os
import pandas as pd
import requests
import time
import tempfile
import json

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_section(title):
    """Imprime seção formatada."""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_core_functionality():
    """Demonstra funcionalidades do core."""
    print_section("CORE FUNCTIONALITY - Análise de Logs")
    
    try:
        from log_analyzer.core import LogAnalyzer
        
        # Criar dados de exemplo
        sample_data = pd.DataFrame({
            'timestamp': [
                '2024-01-01 10:00:00', '2024-01-01 10:00:30', 
                '2024-01-01 10:01:00', '2024-01-01 10:01:30',
                '2024-01-01 10:02:00'
            ],
            'source_ip': [
                '192.168.1.100', '192.168.1.100', '192.168.1.100',
                '10.0.0.50', '172.16.1.200'
            ],
            'destination_ip': [
                '8.8.8.8', '8.8.8.8', '8.8.8.8',
                '1.1.1.1', '208.67.222.222'
            ],
            'action': ['allow', 'block', 'allow', 'allow', 'allow'],
            'status_code': [200, 403, 200, 200, 200],
            'bytes_transferred': [1024, 0, 2048, 512, 1536]
        })
        
        print("✅ Dados de exemplo criados:")
        print(f"   📊 {len(sample_data)} registros de log")
        print(f"   🌐 {sample_data['source_ip'].nunique()} IPs únicos")
        print(f"   📈 {sample_data['bytes_transferred'].sum()} bytes transferidos")
        
        # Inicializar analyzer
        analyzer = LogAnalyzer()
        analyzer.data = sample_data
        print("\n✅ LogAnalyzer inicializado com dados")
        
        # Análise de força bruta
        print("\n🔍 Executando análise de força bruta...")
        brute_force_results = analyzer.analyze_brute_force()
        print(f"   📊 Resultados: {len(brute_force_results)} tentativas suspeitas detectadas")
        
        if len(brute_force_results) > 0:
            for idx, result in brute_force_results.iterrows():
                print(f"   ⚠️  IP: {result['source_ip']} - {result['failed_attempts']} tentativas")
        else:
            print("   ✅ Nenhuma atividade suspeita de força bruta detectada")
        
        # Geração de estatísticas
        print("\n📊 Gerando estatísticas...")
        stats = analyzer.generate_statistics()
        if stats:
            print(f"   📈 Total de eventos: {stats.get('total_events', 0)}")
            print(f"   🌐 IPs únicos: {stats.get('unique_source_ips', 0)}")
            print(f"   ✅ Eventos permitidos: {stats.get('allowed_events', 0)}")
            print(f"   🚫 Eventos bloqueados: {stats.get('blocked_events', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração do core: {e}")
        return False

def demo_geographic_analysis():
    """Demonstra análise geográfica."""
    print_section("GEOGRAPHIC ANALYSIS - Localização de IPs")
    
    try:
        from log_analyzer.geographic import GeographicAnalyzer
        
        geo = GeographicAnalyzer()
        print("✅ GeographicAnalyzer inicializado")
        
        # IPs de exemplo para análise
        test_ips = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        print(f"\n🌍 Analisando localização de {len(test_ips)} IPs...")
        
        for ip in test_ips:
            print(f"\n   🔍 Analisando {ip}...")
            try:
                location = geo.get_ip_location(ip)
                if location:
                    country = location.get('country', 'Desconhecido')
                    city = location.get('city', 'Desconhecida')
                    print(f"   📍 Localização: {city}, {country}")
                else:
                    print("   ⚠️  Localização não encontrada")
            except Exception as e:
                print(f"   ❌ Erro ao obter localização: {e}")
        
        # Análise em lote
        print("\n🌐 Executando análise geográfica em lote...")
        try:
            results = geo.analyze_ips(test_ips[:2])  # Limitando para não sobrecarregar
            print(f"   📊 Resultados: {len(results)} localizações processadas")
            
            for result in results:
                ip = result.get('ip', 'N/A')
                country = result.get('country', 'Desconhecido')
                risk = result.get('risk_level', 'baixo')
                print(f"   🗺️  {ip}: {country} (risco: {risk})")
                
        except Exception as e:
            print(f"   ⚠️  Análise em lote limitada: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise geográfica: {e}")
        return False

def demo_api_functionality():
    """Demonstra funcionalidades da API."""
    print_section("REST API - Endpoints e Funcionalidades")
    
    base_url = "http://127.0.0.1:8000"
    
    # Verificar se API está rodando
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando e respondendo")
            data = response.json()
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            print(f"   🕐 Timestamp: {data.get('timestamp', 'N/A')}")
        else:
            print(f"⚠️  API respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API não está acessível: {e}")
        print("   💡 Certifique-se de que a API está rodando em http://127.0.0.1:8000")
        return False
    
    # Teste do health check
    try:
        print("\n🏥 Testando health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Status: {health_data.get('status', 'N/A')}")
            print(f"   🔧 Versão: {health_data.get('version', 'N/A')}")
            
            components = health_data.get('components', {})
            for component, status in components.items():
                icon = "✅" if status == "available" else "❌"
                print(f"   {icon} {component}: {status}")
    except Exception as e:
        print(f"   ❌ Erro no health check: {e}")
    
    # Teste do endpoint de informações
    try:
        print("\n📋 Obtendo informações da API...")
        response = requests.get(f"{base_url}/api-info", timeout=5)
        if response.status_code == 200:
            info_data = response.json()
            print(f"   📝 Nome: {info_data.get('name', 'N/A')}")
            print(f"   📊 Versão: {info_data.get('version', 'N/A')}")
            
            endpoints = info_data.get('endpoints', {})
            print("   🔗 Endpoints disponíveis:")
            for endpoint, description in endpoints.items():
                print(f"      • {endpoint}: {description}")
    except Exception as e:
        print(f"   ❌ Erro ao obter informações: {e}")
    
    # Teste do endpoint de métricas (se disponível)
    try:
        print("\n📈 Verificando métricas...")
        response = requests.get(f"{base_url}/metrics", timeout=5)
        if response.status_code == 200:
            metrics_data = response.json()
            metrics = metrics_data.get('metrics', {})
            print(f"   ⏱️  Uptime: {metrics.get('uptime_seconds', 0):.1f}s")
            print(f"   📊 Requisições: {metrics.get('request_count', 0)}")
            print(f"   🚀 Tempo médio resposta: {metrics.get('avg_response_time_ms', 0):.1f}ms")
        else:
            print(f"   ⚠️  Métricas não disponíveis (status {response.status_code})")
    except Exception as e:
        print(f"   ℹ️  Métricas não disponíveis: {e}")
    
    return True

def demo_file_processing():
    """Demonstra processamento de arquivos."""
    print_section("FILE PROCESSING - Upload e Análise")
    
    # Criar arquivo CSV de exemplo
    sample_csv = """timestamp,source_ip,destination_ip,action,status_code,bytes_transferred
2024-01-01 10:00:00,192.168.1.100,8.8.8.8,allow,200,1024
2024-01-01 10:00:30,192.168.1.100,8.8.8.8,block,403,0
2024-01-01 10:01:00,192.168.1.100,8.8.8.8,allow,200,2048
2024-01-01 10:01:30,10.0.0.50,1.1.1.1,allow,200,512
2024-01-01 10:02:00,172.16.1.200,208.67.222.222,allow,200,1536
2024-01-01 10:02:30,192.168.1.100,8.8.8.8,block,403,0
2024-01-01 10:03:00,192.168.1.100,8.8.8.8,allow,200,1024"""
    
    try:
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv)
            temp_file = f.name
        
        print(f"✅ Arquivo de exemplo criado: {temp_file}")
        print(f"   📊 Tamanho: {len(sample_csv)} bytes")
        print(f"   📋 Linhas: {sample_csv.count('newline') + 1}")
        
        # Tentar upload via API
        base_url = "http://127.0.0.1:8000"
        try:
            print("\n📤 Testando upload via API...")
            with open(temp_file, 'rb') as file:
                files = {'firewall_log': file}
                response = requests.post(f"{base_url}/analyze/", files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    summary = result.get('summary', {})
                    print("   ✅ Upload bem-sucedido!")
                    print(f"   📊 Arquivos processados: {summary.get('files_processed', 0)}")
                    print(f"   📈 Total de eventos: {summary.get('total_events', 0)}")
                    print(f"   ⏱️  Tempo de processamento: {summary.get('processing_time_seconds', 0):.2f}s")
                    
                    # Mostrar alguns resultados
                    brute_force = result.get('brute_force_attacks', [])
                    if brute_force:
                        print(f"   ⚠️  Ataques de força bruta detectados: {len(brute_force)}")
                    else:
                        print("   ✅ Nenhum ataque de força bruta detectado")
                        
                else:
                    print(f"   ❌ Upload falhou com status {response.status_code}")
                    print(f"   📝 Resposta: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro no upload: {e}")
            
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(temp_file)
                print("   🧹 Arquivo temporário removido")
            except OSError:
                # Ignora erros de remoção de arquivo
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento de arquivo: {e}")
        return False

def demo_cache_system():
    """Demonstra sistema de cache."""
    print_section("CACHE SYSTEM - Performance e Otimização")
    
    try:
        from log_analyzer.cache_system import get_cache
        
        cache = get_cache()
        print("✅ Sistema de cache inicializado")
        
        # Teste de escrita
        print("\n💾 Testando operações de cache...")
        test_data = {
            'ip': '192.168.1.100',
            'location': {'country': 'Brasil', 'city': 'São Paulo'},
            'timestamp': time.time()
        }
        
        cache.set('test_ip_location', test_data)
        print("   ✅ Dados escritos no cache")
        
        # Teste de leitura
        cached_data = cache.get('test_ip_location')
        if cached_data:
            print("   ✅ Dados lidos do cache com sucesso")
            print(f"   📍 IP: {cached_data.get('ip', 'N/A')}")
            print(f"   🌍 País: {cached_data.get('location', {}).get('country', 'N/A')}")
        
        # Mostrar estatísticas
        stats = cache.stats()
        print("\n📊 Estatísticas do cache:")
        print(f"   📈 Hit ratio: {stats.get('hit_ratio', 0):.2%}")
        print(f"   💾 Tamanho atual: {stats.get('hit_count', 0) + stats.get('miss_count', 0)} operações")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de cache: {e}")
        return False

def demo_performance_summary():
    """Mostra resumo de performance."""
    print_section("PERFORMANCE SUMMARY - Métricas Atuais")
    
    try:
        # Ler relatório de performance se existir
        import glob
        performance_files = glob.glob("performance_report_*.txt")
        
        if performance_files:
            latest_report = max(performance_files)
            print(f"✅ Último relatório de performance: {latest_report}")
            
            with open(latest_report, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Extrair métricas importantes
            for line in lines:
                if "Total de operações:" in line:
                    print(f"   📊 {line.strip()}")
                elif "Tempo médio:" in line:
                    print(f"   ⏱️  {line.strip()}")
                elif "Máximo:" in line and "MB" in line:
                    print(f"   💾 Memória {line.strip()}")
        else:
            print("📋 Execute 'python test_performance.py' para gerar métricas detalhadas")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler performance: {e}")
        return False

def run_demos():
    """Executa todas as demonstrações e retorna os resultados."""
    demos = [
        ("Core Functionality", demo_core_functionality),
        ("Geographic Analysis", demo_geographic_analysis),
        ("API Functionality", demo_api_functionality),
        ("File Processing", demo_file_processing),
        ("Cache System", demo_cache_system),
        ("Performance Summary", demo_performance_summary),
    ]
    
    results = []
    for demo_name, demo_func in demos:
        try:
            success = demo_func()
            results.append((demo_name, success))
        except Exception as e:
            print(f"❌ Erro inesperado em {demo_name}: {e}")
            results.append((demo_name, False))
    
    return results

def print_summary(results):
    """Imprime o resumo dos resultados da demonstração."""
    print_header("RESUMO DA DEMONSTRAÇÃO")
    
    passed = 0
    for demo_name, success in results:
        status = "✅ FUNCIONANDO" if success else "❌ COM PROBLEMAS"
        print(f"{demo_name:<20}: {status}")
        if success:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100
    print(f"\n📊 Status Geral: {passed}/{total} módulos funcionando ({success_rate:.0f}%)")
    
    return success_rate

def print_final_status(success_rate):
    """Imprime o status final baseado na taxa de sucesso."""
    if success_rate >= 80:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   • Acesse: http://127.0.0.1:8000/docs para documentação interativa")
        print("   • Teste upload de arquivos via /analyze/")
        print("   • Monitore métricas em /metrics")
    elif success_rate >= 60:
        print("⚠️  SISTEMA FUNCIONANDO COM ALGUMAS LIMITAÇÕES")
        print("💡 Algumas funcionalidades podem ter dependências externas")
    else:
        print("🔧 SISTEMA PRECISA DE CONFIGURAÇÃO")
        print("💡 Verifique dependências e configurações")

def main():
    """Executa demonstração completa."""
    print_header("LOG ANALYZER - DEMONSTRAÇÃO COMPLETA")
    print("🎯 Demonstrando todas as funcionalidades do sistema")
    print("⏱️  Tempo estimado: 2-3 minutos")
    
    # Executar todas as demonstrações
    results = run_demos()
    
    # Imprimir resumo e status final
    success_rate = print_summary(results)
    print_final_status(success_rate)
    
    return 0 if success_rate >= 60 else 1

if __name__ == "__main__":
    sys.exit(main())