#!/usr/bin/env python
"""
Exemplo de cliente para a API Log Analyzer

Este script demonstra como usar a API Log Analyzer para enviar logs
e receber análises de segurança.

Exemplos de uso:
    python examples/api_client_example.py --test-status
    python examples/api_client_example.py --analyze data/sample_firewall.csv
    python examples/api_client_example.py --analyze data/firewall.csv data/auth.csv
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    print("❌ Requests não está instalado. Execute: pip install requests")
    sys.exit(1)


class LogAnalyzerAPIClient:
    """Cliente para interagir com a API Log Analyzer."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Inicializar cliente da API.
        
        Args:
            base_url: URL base da API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obter status da API.
        
        Returns:
            Dict: Status da API
        """
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao conectar com a API: {e}"}
    
    def get_health(self) -> Dict[str, Any]:
        """
        Verificar saúde da API.
        
        Returns:
            Dict: Informações de saúde
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao verificar saúde da API: {e}"}
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Obter informações sobre a API.
        
        Returns:
            Dict: Informações da API
        """
        try:
            response = self.session.get(f"{self.base_url}/api-info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao obter informações da API: {e}"}
    
    def analyze_logs(
        self,
        firewall_log_path: Optional[str] = None,
        auth_log_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analisar logs enviando arquivos para a API.
        
        Args:
            firewall_log_path: Caminho para o log de firewall
            auth_log_path: Caminho para o log de autenticação
            
        Returns:
            Dict: Resultados da análise
        """
        if not firewall_log_path and not auth_log_path:
            return {"error": "Pelo menos um arquivo de log deve ser fornecido"}
        
        files = {}
        
        try:
            if firewall_log_path:
                firewall_path = Path(firewall_log_path)
                if not firewall_path.exists():
                    return {"error": f"Arquivo de firewall não encontrado: {firewall_log_path}"}
                files['firewall_log'] = (
                    firewall_path.name,
                    open(firewall_path, 'rb'),
                    'application/octet-stream'
                )
            
            if auth_log_path:
                auth_path = Path(auth_log_path)
                if not auth_path.exists():
                    return {"error": f"Arquivo de auth não encontrado: {auth_log_path}"}
                files['auth_log'] = (
                    auth_path.name,
                    open(auth_path, 'rb'),
                    'application/octet-stream'
                )
            
            response = self.session.post(f"{self.base_url}/analyze/", files=files)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao analisar logs: {e}"}
        finally:
            # Fechar arquivos abertos
            for file_info in files.values():
                if hasattr(file_info[1], 'close'):
                    file_info[1].close()


def print_json_pretty(data: Dict[str, Any]) -> None:
    """Imprimir JSON de forma formatada."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def create_sample_data() -> None:
    """Criar dados de exemplo para testes."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Criar log de firewall de exemplo
    firewall_sample = data_dir / "sample_firewall.csv"
    if not firewall_sample.exists():
        firewall_content = """timestamp,source_ip,destination_ip,port,protocol,action
2024-01-01 10:00:01,192.168.1.100,10.0.0.1,80,TCP,ALLOW
2024-01-01 10:00:02,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:03,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:04,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:05,198.51.100.10,10.0.0.1,443,TCP,ALLOW
2024-01-01 10:00:06,203.0.113.5,10.0.0.1,21,TCP,DENY
2024-01-01 10:00:07,203.0.113.5,10.0.0.1,23,TCP,DENY
2024-01-01 10:00:08,203.0.113.5,10.0.0.1,25,TCP,DENY"""
        
        firewall_sample.write_text(firewall_content)
        print(f"✅ Arquivo de exemplo criado: {firewall_sample}")
    
    # Criar log de autenticação de exemplo
    auth_sample = data_dir / "sample_auth.csv"
    if not auth_sample.exists():
        auth_content = """timestamp,username,source_ip,event_type,success
2024-01-01 10:01:01,admin,192.168.1.50,login,true
2024-01-01 10:01:05,admin,203.0.113.5,login,false
2024-01-01 10:01:10,admin,203.0.113.5,login,false
2024-01-01 10:01:15,admin,203.0.113.5,login,false
2024-01-01 10:01:20,user1,192.168.1.60,login,true
2024-01-01 10:01:25,admin,203.0.113.5,login,false
2024-01-01 10:01:30,admin,203.0.113.5,login,false"""
        
        auth_sample.write_text(auth_content)
        print(f"✅ Arquivo de exemplo criado: {auth_sample}")


def main():
    """Função principal do cliente de exemplo."""
    parser = argparse.ArgumentParser(
        description="Cliente de exemplo para a API Log Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="URL base da API (default: http://127.0.0.1:8000)"
    )
    
    parser.add_argument(
        "--test-status",
        action="store_true",
        help="Testar status e saúde da API"
    )
    
    parser.add_argument(
        "--create-samples",
        action="store_true",
        help="Criar arquivos de exemplo para testes"
    )
    
    parser.add_argument(
        "--analyze",
        nargs='+',
        help="Analisar logs (forneça 1 ou 2 arquivos: firewall e/ou auth)"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Obter informações sobre a API"
    )
    
    args = parser.parse_args()
    
    # Criar cliente
    client = LogAnalyzerAPIClient(args.url)
    
    if args.create_samples:
        create_sample_data()
        return
    
    if args.test_status:
        print("🔍 Testando status da API...")
        status = client.get_status()
        print_json_pretty(status)
        
        print("\n🏥 Verificando saúde da API...")
        health = client.get_health()
        print_json_pretty(health)
        return
    
    if args.info:
        print("ℹ️ Obtendo informações da API...")
        info = client.get_api_info()
        print_json_pretty(info)
        return
    
    if args.analyze:
        print(f"📊 Analisando logs: {args.analyze}")
        
        firewall_path = None
        auth_path = None
        
        if len(args.analyze) == 1:
            # Detectar tipo de arquivo pelo nome
            file_path = args.analyze[0]
            if 'firewall' in file_path.lower() or 'fw' in file_path.lower():
                firewall_path = file_path
            else:
                auth_path = file_path
        elif len(args.analyze) == 2:
            firewall_path = args.analyze[0]
            auth_path = args.analyze[1]
        else:
            print("❌ Máximo de 2 arquivos são suportados")
            return
        
        results = client.analyze_logs(firewall_path, auth_path)
        print_json_pretty(results)
        return
    
    # Se nenhuma ação específica, mostrar ajuda
    parser.print_help()


if __name__ == "__main__":
    main()