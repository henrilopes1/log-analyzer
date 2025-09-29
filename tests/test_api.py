#!/usr/bin/env python
"""
Testes automatizados para a API Log Analyzer

Este script executa testes abrangentes da API REST para verificar
funcionalidade, performance e casos de erro.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    import requests
except ImportError:
    print("❌ Requests não está instalado. Execute: pip install requests")
    sys.exit(1)


class APITester:
    """Classe para executar testes automatizados da API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log resultado de um teste."""
        self.results["total"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
            print(f"❌ {test_name}: {details}")
    
    def test_api_status(self) -> None:
        """Testar endpoint de status."""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            success = response.status_code == 200 and "status" in response.json()
            details = "" if success else f"Status: {response.status_code}"
            self.log_test("API Status Endpoint", success, details)
        except Exception as e:
            self.log_test("API Status Endpoint", False, str(e))
    
    def test_health_check(self) -> None:
        """Testar endpoint de health check."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("status") == "healthy")
            details = "" if success else f"Status: {response.status_code}, Data: {data}"
            self.log_test("Health Check Endpoint", success, details)
        except Exception as e:
            self.log_test("Health Check Endpoint", False, str(e))
    
    def test_api_info(self) -> None:
        """Testar endpoint de informações da API."""
        try:
            response = self.session.get(f"{self.base_url}/api-info", timeout=5)
            data = response.json()
            success = (response.status_code == 200 and 
                      "name" in data and "endpoints" in data)
            details = "" if success else f"Status: {response.status_code}"
            self.log_test("API Info Endpoint", success, details)
        except Exception as e:
            self.log_test("API Info Endpoint", False, str(e))
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Criar arquivo temporário para testes."""
        test_dir = Path("temp_test_data")
        test_dir.mkdir(exist_ok=True)
        
        file_path = test_dir / filename
        file_path.write_text(content)
        return file_path
    
    def test_analyze_without_files(self) -> None:
        """Testar análise sem arquivos (deve falhar)."""
        try:
            response = self.session.post(f"{self.base_url}/analyze/", timeout=10)
            success = response.status_code == 400
            details = "" if success else f"Status: {response.status_code} (esperado 400)"
            self.log_test("Analyze Without Files (Error Case)", success, details)
        except Exception as e:
            self.log_test("Analyze Without Files (Error Case)", False, str(e))
    
    def test_analyze_with_firewall_log(self) -> None:
        """Testar análise com log de firewall."""
        try:
            # Criar arquivo de teste
            firewall_content = """timestamp,source_ip,destination_ip,port,protocol,action
2024-01-01 10:00:01,192.168.1.100,10.0.0.1,80,TCP,ALLOW
2024-01-01 10:00:02,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:03,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:04,203.0.113.5,10.0.0.1,22,TCP,DENY"""
            
            test_file = self.create_test_file("test_firewall.csv", firewall_content)
            
            with open(test_file, 'rb') as f:
                files = {'firewall_log': ('test_firewall.csv', f, 'text/csv')}
                response = self.session.post(
                    f"{self.base_url}/analyze/", 
                    files=files, 
                    timeout=30
                )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "summary" in data and "firewall_analysis" in data
            
            details = "" if success else f"Status: {response.status_code}"
            self.log_test("Analyze Firewall Log", success, details)
            
            # Limpar arquivo de teste
            test_file.unlink(missing_ok=True)
            
        except Exception as e:
            self.log_test("Analyze Firewall Log", False, str(e))
    
    def test_analyze_with_auth_log(self) -> None:
        """Testar análise com log de autenticação."""
        try:
            # Criar arquivo de teste
            auth_content = """timestamp,username,source_ip,event_type,success
2024-01-01 10:01:01,admin,192.168.1.50,login,true
2024-01-01 10:01:05,admin,203.0.113.5,login,false
2024-01-01 10:01:10,admin,203.0.113.5,login,false
2024-01-01 10:01:15,admin,203.0.113.5,login,false"""
            
            test_file = self.create_test_file("test_auth.csv", auth_content)
            
            with open(test_file, 'rb') as f:
                files = {'auth_log': ('test_auth.csv', f, 'text/csv')}
                response = self.session.post(
                    f"{self.base_url}/analyze/", 
                    files=files, 
                    timeout=30
                )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "summary" in data
            
            details = "" if success else f"Status: {response.status_code}"
            self.log_test("Analyze Auth Log", success, details)
            
            # Limpar arquivo de teste
            test_file.unlink(missing_ok=True)
            
        except Exception as e:
            self.log_test("Analyze Auth Log", False, str(e))
    
    def test_analyze_with_both_logs(self) -> None:
        """Testar análise com ambos os logs."""
        try:
            firewall_content = """timestamp,source_ip,destination_ip,port,protocol,action
2024-01-01 10:00:01,203.0.113.5,10.0.0.1,22,TCP,DENY
2024-01-01 10:00:02,203.0.113.5,10.0.0.1,22,TCP,DENY"""
            
            auth_content = """timestamp,username,source_ip,event_type,success
2024-01-01 10:01:05,admin,203.0.113.5,login,false
2024-01-01 10:01:10,admin,203.0.113.5,login,false"""
            
            fw_file = self.create_test_file("test_fw.csv", firewall_content)
            auth_file = self.create_test_file("test_auth.csv", auth_content)
            
            with open(fw_file, 'rb') as f1, open(auth_file, 'rb') as f2:
                files = {
                    'firewall_log': ('test_fw.csv', f1, 'text/csv'),
                    'auth_log': ('test_auth.csv', f2, 'text/csv')
                }
                response = self.session.post(
                    f"{self.base_url}/analyze/", 
                    files=files, 
                    timeout=30
                )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = ("summary" in data and 
                          data["summary"]["files_processed"] == 2)
            
            details = "" if success else f"Status: {response.status_code}"
            self.log_test("Analyze Both Logs", success, details)
            
            # Limpar arquivos de teste
            fw_file.unlink(missing_ok=True)
            auth_file.unlink(missing_ok=True)
            
        except Exception as e:
            self.log_test("Analyze Both Logs", False, str(e))
    
    def test_invalid_file_format(self) -> None:
        """Testar upload de arquivo com formato inválido."""
        try:
            # Criar arquivo com formato inválido
            invalid_content = "Este não é um CSV nem JSON válido!"
            test_file = self.create_test_file("test_invalid.txt", invalid_content)
            
            with open(test_file, 'rb') as f:
                files = {'firewall_log': ('test_invalid.txt', f, 'text/plain')}
                response = self.session.post(
                    f"{self.base_url}/analyze/", 
                    files=files, 
                    timeout=10
                )
            
            success = response.status_code == 400
            details = "" if success else f"Status: {response.status_code} (esperado 400)"
            self.log_test("Invalid File Format (Error Case)", success, details)
            
            # Limpar arquivo de teste
            test_file.unlink(missing_ok=True)
            
        except Exception as e:
            self.log_test("Invalid File Format (Error Case)", False, str(e))
    
    def test_performance(self) -> None:
        """Testar performance da API."""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            success = response.status_code == 200 and response_time < 2.0
            
            details = f"Response time: {response_time:.2f}s" if not success else ""
            self.log_test("API Response Time < 2s", success, details)
            
        except Exception as e:
            self.log_test("API Response Time < 2s", False, str(e))
    
    def cleanup(self) -> None:
        """Limpar arquivos temporários."""
        test_dir = Path("temp_test_data")
        if test_dir.exists():
            for file in test_dir.iterdir():
                file.unlink(missing_ok=True)
            test_dir.rmdir()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executar todos os testes."""
        print("🚀 Iniciando testes da API Log Analyzer...")
        print(f"📍 URL base: {self.base_url}")
        print("=" * 50)
        
        try:
            # Testes básicos
            self.test_api_status()
            self.test_health_check()
            self.test_api_info()
            self.test_performance()
            
            # Testes de análise
            self.test_analyze_without_files()
            self.test_analyze_with_firewall_log()
            self.test_analyze_with_auth_log()
            self.test_analyze_with_both_logs()
            self.test_invalid_file_format()
            
        finally:
            self.cleanup()
        
        print("=" * 50)
        print(f"📊 Resultados dos testes:")
        print(f"   Total: {self.results['total']}")
        print(f"   ✅ Passou: {self.results['passed']}")
        print(f"   ❌ Falhou: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n📋 Erros encontrados:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total']) * 100
        print(f"\n🎯 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ API está funcionando adequadamente!")
        else:
            print("⚠️ API precisa de atenção - muitos testes falharam")
        
        return self.results


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Executar testes automatizados da API Log Analyzer"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="URL base da API (default: http://127.0.0.1:8000)"
    )
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    results = tester.run_all_tests()
    
    # Exit code baseado nos resultados
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == "__main__":
    main()