"""
Módulo de análise geográfica do Log Analyzer
"""

import json
import time
from collections import Counter
from typing import Any, Dict, List, Optional, Set

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import DEFAULT_CONFIG


class GeographicAnalyzer:
    """Classe para análise geográfica de IPs suspeitos"""

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, console: Optional[Console] = None
    ):
        """
        Inicializa o analisador geográfico

        Args:
            config: Configurações customizadas
            console: Instância do console Rich
        """
        self.config = config or DEFAULT_CONFIG
        self.console = console or Console()
        self.ip_location_cache = {}

        # Configurações geográficas
        geo_config = self.config["geographic"]
        self.enabled = geo_config["enabled"]
        self.timeout = geo_config["timeout_seconds"]
        self.api_url = geo_config["api_url"]
        self.rate_limit_delay = geo_config["rate_limit_delay"]
        self.high_risk_countries = geo_config["high_risk_countries"]

    def get_ip_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de geolocalização para um IP

        Args:
            ip_address: Endereço IP

        Returns:
            Dicionário com informações de localização ou None
        """
        if not self.enabled:
            return None

        # Verificar cache
        if ip_address in self.ip_location_cache:
            return self.ip_location_cache[ip_address]

        # Ignorar IPs privados
        if self._is_private_ip(ip_address):
            return None

        try:
            # Fazer requisição para API
            url = f"{self.api_url}/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,lat,lon,isp,org,as"
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "success":
                    location_info = {
                        "country": data.get("country", "Desconhecido"),
                        "country_code": data.get("countryCode", "XX"),
                        "region": data.get("regionName", "Desconhecido"),
                        "city": data.get("city", "Desconhecido"),
                        "latitude": data.get("lat", 0.0),
                        "longitude": data.get("lon", 0.0),
                        "isp": data.get("isp", "Desconhecido"),
                        "organization": data.get("org", "Desconhecido"),
                        "as_info": data.get("as", "Desconhecido"),
                    }

                    # Adicionar ao cache
                    self.ip_location_cache[ip_address] = location_info

                    # Rate limiting
                    time.sleep(self.rate_limit_delay)

                    return location_info
                else:
                    self.console.print(
                        f"[yellow]⚠️ Erro na geolocalização de {ip_address}: {data.get('message', 'Erro desconhecido')}[/yellow]"
                    )

        except requests.exceptions.Timeout:
            self.console.print(
                f"[yellow]⚠️ Timeout na consulta de geolocalização para {ip_address} após {self.timeout}s[/yellow]"
            )
        except requests.exceptions.ConnectionError:
            self.console.print(
                f"[red]❌ Erro de conexão na geolocalização de {ip_address}: Não foi possível conectar à API de geolocalização[/red]"
            )
        except requests.exceptions.HTTPError as e:
            self.console.print(
                f"[red]❌ Erro HTTP na geolocalização de {ip_address}: {e.response.status_code} - {e.response.reason}[/red]"
            )
        except requests.exceptions.RequestException as e:
            self.console.print(
                f"[yellow]⚠️ Erro de requisição na geolocalização de {ip_address}: {type(e).__name__} - {str(e)}[/yellow]"
            )
        except json.JSONDecodeError:
            self.console.print(
                f"[red]❌ Erro ao decodificar resposta JSON para {ip_address}: Resposta inválida da API de geolocalização[/red]"
            )
        except Exception as e:
            self.console.print(
                f"[red]❌ Erro inesperado na geolocalização de {ip_address}: {type(e).__name__} - {str(e)}[/red]"
            )

        return None

    def _is_private_ip(self, ip: str) -> bool:
        """
        Verifica se o IP é privado/reservado

        Args:
            ip: Endereço IP

        Returns:
            True se o IP for privado
        """
        try:
            parts = [int(x) for x in ip.split(".")]

            # Redes privadas RFC 1918
            if parts[0] == 10:
                return True
            if parts[0] == 172 and 16 <= parts[1] <= 31:
                return True
            if parts[0] == 192 and parts[1] == 168:
                return True

            # Localhost
            if parts[0] == 127:
                return True

            # Link-local
            if parts[0] == 169 and parts[1] == 254:
                return True

            return False

        except (ValueError, IndexError):
            return True  # Se não conseguir parsear, assumir como privado

    def analyze_geographic_patterns(self, suspect_ips: Set[str]) -> None:
        """
        Analisa padrões geográficos de IPs suspeitos

        Args:
            suspect_ips: Conjunto de IPs suspeitos para análise
        """
        if not self.enabled:
            self.console.print("[yellow]⏭️ Análise geográfica desabilitada[/yellow]")
            return

        if not suspect_ips:
            self.console.print(
                "[green]✅ Nenhum IP suspeito para análise geográfica[/green]"
            )
            return

        self.console.print("\n🌍 ANÁLISE GEOGRÁFICA\n", style="bold blue")
        self.console.print(f"🔍 Analisando {len(suspect_ips)} IPs suspeitos...\n")

        # Coletar dados geográficos
        geo_data = []
        countries_count = Counter()

        for ip in suspect_ips:
            location = self.get_ip_location(ip)
            if location:
                geo_data.append({"ip": ip, **location})
                countries_count[location["country"]] += 1

        if not geo_data:
            self.console.print(
                "[yellow]⚠️ Não foi possível obter dados geográficos[/yellow]"
            )
            return

        # Mostrar distribuição por país
        self._display_country_distribution(countries_count, len(geo_data))

        # Mostrar detalhes por IP
        self._display_ip_details(geo_data)

        # Mostrar recomendações
        self._display_recommendations(geo_data)

    def _display_country_distribution(
        self, countries_count: Counter, total_ips: int
    ) -> None:
        """Exibe distribuição geográfica por país"""
        table = Table(
            title="🌎 Distribuição Geográfica dos IPs Suspeitos", box=box.HEAVY
        )
        table.add_column("País", style="cyan bold")
        table.add_column("Código", style="yellow", justify="center")
        table.add_column("Quantidade", style="red bold", justify="center")
        table.add_column("Percentual", style="green", justify="center")
        table.add_column("Status", style="white", justify="center")

        for country, count in countries_count.most_common():
            percentage = (count / total_ips) * 100

            # Encontrar código do país
            country_code = "XX"
            for geo_item in self.ip_location_cache.values():
                if geo_item and geo_item.get("country") == country:
                    country_code = geo_item.get("country_code", "XX")
                    break

            # Determinar status de risco
            if country_code in self.high_risk_countries:
                status = "🚨 Alto Risco"
            elif percentage > 30:
                status = "⚠️ Concentração Alta"
            else:
                status = "✅ Normal"

            table.add_row(
                country, country_code, str(count), f"{percentage:.1f}%", status
            )

        self.console.print(table)
        self.console.print()

    def _display_ip_details(self, geo_data: List[Dict[str, Any]]) -> None:
        """Exibe detalhes geográficos de cada IP"""
        self.console.print("🔍 DETALHES GEOGRÁFICOS DOS IPS\n", style="bold yellow")

        table = Table(title="📍 Informações Detalhadas por IP", box=box.ROUNDED)
        table.add_column("IP", style="yellow bold", no_wrap=True)
        table.add_column("País/Região", style="cyan")
        table.add_column("Cidade", style="white")
        table.add_column("ISP", style="blue")
        table.add_column("Coordenadas", style="green")
        table.add_column("Risco", style="red", justify="center")

        for item in geo_data:
            # Calcular fatores de risco
            risk_factors = []

            if item["country_code"] in self.high_risk_countries:
                risk_factors.append("País Alto Risco")

            org_lower = item["organization"].lower()
            if any(
                term in org_lower
                for term in ["proxy", "vpn", "hosting", "server", "datacenter"]
            ):
                risk_factors.append("VPN/Proxy/Hosting")

            # Determinar nível de risco
            if len(risk_factors) >= 2:
                risk_level = "🚨 Alto"
            elif len(risk_factors) == 1:
                risk_level = "⚠️ Médio"
            else:
                risk_level = "✅ Baixo"

            # Formatar dados para exibição
            location = f"{item['country']}/{item['region']}"
            coords = f"{item['latitude']:.2f}, {item['longitude']:.2f}"
            isp_truncated = (
                item["isp"][:25] + "..." if len(item["isp"]) > 25 else item["isp"]
            )

            table.add_row(
                item["ip"], location, item["city"], isp_truncated, coords, risk_level
            )

        self.console.print(table)
        self.console.print()

    def _display_recommendations(self, geo_data: List[Dict[str, Any]]) -> None:
        """Exibe recomendações baseadas na análise geográfica"""
        recommendations = Text()
        recommendations.append(
            "💡 RECOMENDAÇÕES BASEADAS NA ANÁLISE GEOGRÁFICA:\n\n", style="bold cyan"
        )

        # IPs de países de alto risco
        high_risk_ips = [
            item
            for item in geo_data
            if item["country_code"] in self.high_risk_countries
        ]

        if high_risk_ips:
            recommendations.append(
                "🚨 IPs de países de alto risco detectados:\n", style="bold red"
            )
            for item in high_risk_ips[:5]:  # Mostrar apenas os primeiros 5
                recommendations.append(
                    f"   • {item['ip']} ({item['country']})\n", style="red"
                )
            recommendations.append("\n")

        # IPs usando VPN/Proxy/Hosting
        suspicious_orgs = [
            item
            for item in geo_data
            if any(
                term in item["organization"].lower()
                for term in ["proxy", "vpn", "hosting", "server", "datacenter"]
            )
        ]

        if suspicious_orgs:
            recommendations.append(
                "🔒 IPs suspeitos por tipo de organização:\n", style="bold yellow"
            )
            for item in suspicious_orgs[:3]:
                recommendations.append(
                    f"   • {item['ip']} - {item['organization']}\n", style="yellow"
                )
            recommendations.append("\n")

        # Recomendações gerais
        recommendations.append("🛡️ Ações recomendadas:\n", style="bold white")

        if high_risk_ips:
            recommendations.append(
                "   • Implementar geo-blocking para países de alto risco\n",
                style="white",
            )

        if suspicious_orgs:
            recommendations.append(
                "   • Monitorar conexões através de VPN/Proxy/Hosting\n", style="white"
            )

        recommendations.append(
            "   • Configurar alertas para mudanças geográficas bruscas\n", style="white"
        )
        recommendations.append(
            "   • Considerar autenticação adicional para localizações incomuns\n",
            style="white",
        )
        recommendations.append(
            "   • Implementar rate limiting baseado em geolocalização\n", style="white"
        )

        # Estatísticas de concentração
        countries_count = Counter(item["country"] for item in geo_data)
        if countries_count.most_common(1)[0][1] > len(geo_data) * 0.5:
            recommendations.append(
                "   • Avaliar bloqueio temporário do país com maior concentração\n",
                style="white",
            )

        panel = Panel(
            recommendations,
            title="🌍 Análise Geográfica Concluída",
            border_style="cyan",
            expand=False,
        )

        self.console.print(panel)

    def analyze_ips(self, ip_list: List[str]) -> List[Dict[str, Any]]:
        """
        Analisa uma lista de IPs geograficamente

        Args:
            ip_list: Lista de endereços IP

        Returns:
            Lista com informações geográficas dos IPs
        """
        results = []

        for ip in ip_list:
            location_info = self.get_ip_location(ip)
            if location_info:
                results.append(
                    {
                        "ip": ip,
                        "country": location_info.get("country", "Desconhecido"),
                        "city": location_info.get("city", "Desconhecido"),
                        "latitude": location_info.get("latitude", 0.0),
                        "longitude": location_info.get("longitude", 0.0),
                        "risk_level": (
                            "high"
                            if location_info.get("country") in self.high_risk_countries
                            else "low"
                        ),
                    }
                )

        return results
