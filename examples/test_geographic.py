import sys
import json
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH para importar corretamente a pasta 'src'
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.log_analyzer.geographic import GeographicAnalyzer

def main():
    print("🌍 Iniciando teste do módulo de análise geográfica (geographic.py)...\n")
    
    # 1. Instanciando o analisador
    # O GeographicAnalyzer normalmente busca dados em uma API pública como ip-api.com
    analyzer = GeographicAnalyzer()
    
    # 2. Definindo uma lista de IPs variados para teste
    test_ips = [
        "8.8.8.8",         # Google DNS (Estados Unidos)
        "1.1.1.1",         # Cloudflare (Estados Unidos)
        "187.112.50.12",   # IP Aleatório (Brasil)
        "192.168.0.1",     # IP Privado (rede local, deve ser ignorado)
        "203.0.113.5"      # IP de Documentação/Mock (IP suspeito dos nossos logs de exemplo)
    ]
    
    print(f"🔍 Testando os seguintes IPs: {', '.join(test_ips)}\n")
    
    # 3. Teste 1: Consulta IP a IP usando get_ip_location()
    print("=" * 60)
    print("TESTE 1: Consulta individual por IP")
    print("=" * 60)
    
    for ip in test_ips:
        print(f"\n📡 Buscando dados para: {ip}")
        data = analyzer.get_ip_location(ip)
        
        if data:
            print(f"  📍 Localização: {data.get('city')} / {data.get('region')} - {data.get('country')} ({data.get('country_code')})")
            print(f"  🌐 Provedor (ISP): {data.get('isp')} / {data.get('organization')}")
            print(f"  🗺️ Coordenadas: [{data.get('latitude')}, {data.get('longitude')}]")
        else:
            print("  ❌ Nenhuma localização ou IP privado/inválido ignorado pela ferramenta.")
            
    # 4. Teste 2: Formatação final para a API (analyze_ips ou analyze_geographic_patterns)
    print("\n" + "=" * 60)
    print("TESTE 2: Análise em lote (Como é enviado pra API/Frontend)")
    print("=" * 60)
    
    try:
        # Tenta executar o analyze_ips utilizado pelo seu run_api.py
        results = analyzer.analyze_ips(test_ips)
        print("\nResultado JSON da Análise em Lote:\n")
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except AttributeError:
        # Caso o analyze_ips chame outra função internamente
        print("Usando o output rico em terminal de analyze_geographic_patterns():")
        analyzer.analyze_geographic_patterns(set(test_ips))

if __name__ == "__main__":
    main()
