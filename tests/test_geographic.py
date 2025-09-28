"""
Testes para o módulo geographic.py
"""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from log_analyzer.geographic import GeographicAnalyzer


class TestGeographicAnalyzer:
    """Testes para a classe GeographicAnalyzer"""

    def test_init_default(self):
        """Testa inicialização com valores padrão"""
        analyzer = GeographicAnalyzer()

        assert analyzer.config is not None
        assert analyzer.console is not None
        assert analyzer.ip_location_cache == {}

    def test_init_with_config(self):
        """Testa inicialização com configuração customizada"""
        config = {
            "geographic": {
                "enabled": False,
                "timeout_seconds": 10,
                "api_url": "test_url",
                "rate_limit_delay": 2,
                "high_risk_countries": ["Test"],
            }
        }
        analyzer = GeographicAnalyzer(config=config)

        assert analyzer.enabled is False
        assert analyzer.timeout == 10


class TestGetIpLocation:
    """Testes para get_ip_location"""

    @patch("requests.get")
    def test_get_valid_ip_location(self, mock_get):
        """Testa busca de localização para IP válido"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            "country": "United States",
            "regionName": "California",
            "city": "San Francisco",
            "lat": 37.7749,
            "lon": -122.4194,
            "status": "success",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        analyzer = GeographicAnalyzer()
        result = analyzer.get_ip_location("8.8.8.8")

        assert result is not None
        assert result["country"] == "United States"
        assert result["city"] == "San Francisco"
        assert "latitude" in result
        assert "longitude" in result

    def test_private_ip_address(self):
        """Testa IP privado (não deve fazer requisição)"""
        analyzer = GeographicAnalyzer()
        private_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]

        for ip in private_ips:
            result = analyzer.get_ip_location(ip)
            assert result is None

    @patch("requests.get")
    def test_api_request_failure(self, mock_get):
        """Testa falha na requisição da API"""
        mock_get.side_effect = Exception("Connection error")

        analyzer = GeographicAnalyzer()
        result = analyzer.get_ip_location("8.8.8.8")

        assert result is None


class TestAnalyzeIps:
    """Testes para analyze_ips"""

    @patch.object(GeographicAnalyzer, "get_ip_location")
    def test_analyze_valid_ips(self, mock_get_location):
        """Testa análise de IPs válidos"""
        # Mock das respostas de localização
        mock_get_location.return_value = {
            "country": "United States",
            "regionName": "California",
            "city": "San Francisco",
            "lat": 37.7749,
            "lon": -122.4194,
        }

        analyzer = GeographicAnalyzer()
        ips = ["8.8.8.8", "8.8.4.4"]

        results = analyzer.analyze_ips(ips)

        assert results is not None
        assert len(results) == 2

    @patch.object(GeographicAnalyzer, "get_ip_location")
    def test_analyze_private_ips(self, mock_get_location):
        """Testa análise com IPs privados"""
        mock_get_location.return_value = None

        analyzer = GeographicAnalyzer()
        ips = ["192.168.1.1", "10.0.0.1"]

        results = analyzer.analyze_ips(ips)

        # Deve processar mas sem dados de localização
        assert isinstance(results, list)


class TestHighRiskDetection:
    """Testes para detecção de países de alto risco"""

    def test_high_risk_country_detection(self):
        """Testa detecção de países de alto risco"""
        config = {
            "geographic": {
                "enabled": True,
                "timeout_seconds": 5,
                "api_url": "test_url",
                "rate_limit_delay": 1,
                "high_risk_countries": ["China", "Russia", "North Korea"],
            }
        }

        analyzer = GeographicAnalyzer(config=config)

        # Testar se países de alto risco são detectados corretamente
        assert "China" in analyzer.high_risk_countries
        assert "Russia" in analyzer.high_risk_countries
        assert "United States" not in analyzer.high_risk_countries


class TestCaching:
    """Testes para cache de IPs"""

    @patch("requests.get")
    def test_ip_location_caching(self, mock_get):
        """Testa cache de localização de IPs"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            "country": "United States",
            "city": "Mountain View",
            "lat": 37.386,
            "lon": -122.084,
            "status": "success",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        analyzer = GeographicAnalyzer()

        # Primeira chamada
        result1 = analyzer.get_ip_location("8.8.8.8")

        # Segunda chamada (deve usar cache)
        result2 = analyzer.get_ip_location("8.8.8.8")

        # Deve fazer apenas uma requisição HTTP devido ao cache
        assert mock_get.call_count == 1
        assert result1 == result2
        assert "8.8.8.8" in analyzer.ip_location_cache


class TestErrorHandling:
    """Testes para tratamento de erros"""

    @patch("requests.get")
    def test_api_timeout(self, mock_get):
        """Testa timeout da API"""
        mock_get.side_effect = Exception("Timeout")

        analyzer = GeographicAnalyzer()
        result = analyzer.get_ip_location("8.8.8.8")

        assert result is None

    @patch("requests.get")
    def test_api_rate_limit(self, mock_get):
        """Testa limite de taxa da API"""
        mock_response = Mock()
        mock_response.status_code = 429  # Too Many Requests
        mock_get.return_value = mock_response

        analyzer = GeographicAnalyzer()
        result = analyzer.get_ip_location("8.8.8.8")

        assert result is None

    def test_empty_ip_list(self):
        """Testa análise com lista vazia de IPs"""
        analyzer = GeographicAnalyzer()
        results = analyzer.analyze_ips([])

        assert isinstance(results, list)
        assert len(results) == 0


class TestIntegration:
    """Testes de integração para GeographicAnalyzer"""

    @patch.object(GeographicAnalyzer, "get_ip_location")
    def test_complete_geographic_workflow(self, mock_get_location):
        """Testa fluxo completo de análise geográfica"""
        # Mock das respostas
        mock_locations = [
            {
                "country": "United States",
                "regionName": "California",
                "city": "San Francisco",
                "lat": 37.7749,
                "lon": -122.4194,
            },
            {
                "country": "Brazil",
                "regionName": "São Paulo",
                "city": "São Paulo",
                "lat": -23.5505,
                "lon": -46.6333,
            },
        ]
        mock_get_location.side_effect = mock_locations

        analyzer = GeographicAnalyzer()

        # Executar análise completa
        ips = ["8.8.8.8", "200.100.50.25"]
        results = analyzer.analyze_ips(ips)

        # Verificar resultados
        assert isinstance(results, list)
        assert len(results) == 2
