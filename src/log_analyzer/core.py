"""
Classe principal do Log Analyzer
"""

import json
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import DEFAULT_CONFIG, SUPPORTED_SCHEMAS
from .utils import (
    calculate_risk_score,
    clean_ip_address,
    ensure_directory_exists,
    format_duration,
    generate_timestamped_filename,
    load_data_file,
    parse_timestamp,
    setup_logging,
    validate_required_columns,
)


class LogAnalyzer:
    """Classe principal para análise de logs de segurança"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o analisador de logs

        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or DEFAULT_CONFIG
        self.console = Console()
        self.logger = setup_logging(self.config.get("logging"))

        # Dados de análise
        self.data = None  # DataFrame principal
        self.failed_logins = []
        self.ip_access_count = Counter()
        self.brute_force_attempts = []
        self.port_scan_attempts = []
        self.ip_location_cache = {}

        # Estatísticas
        self.analysis_stats = {
            "total_logs_processed": 0,
            "firewall_logs": 0,
            "auth_logs": 0,
            "suspect_ips_found": 0,
            "analysis_start_time": None,
            "analysis_end_time": None,
        }

    def load_log_file(
        self, file_path: str, log_type: str = "unknown"
    ) -> Optional[pd.DataFrame]:
        """
        Carrega um arquivo de logs com validação

        Args:
            file_path: Caminho para o arquivo
            log_type: Tipo do log ('firewall' ou 'authentication')

        Returns:
            DataFrame com os dados ou None se houver erro
        """
        try:
            self.logger.info(f"Carregando arquivo: {file_path}")
            df = load_data_file(file_path)

            if df is None or df.empty:
                self.console.print(f"[red]❌ Arquivo vazio: {file_path}[/red]")
                return None

            # Validar colunas se o tipo for conhecido
            if log_type in SUPPORTED_SCHEMAS:
                required_cols = SUPPORTED_SCHEMAS[log_type]["required_columns"]
                validate_required_columns(df, required_cols, log_type)

            # Limpar e validar IPs
            if "source_ip" in df.columns:
                df["source_ip"] = df["source_ip"].apply(clean_ip_address)
                df = df[df["source_ip"] != ""]  # Remover IPs inválidos

            # Converter timestamps
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                df = df.dropna(
                    subset=["timestamp"]
                )  # Remover registros com timestamp inválido

            self.console.print(f"[green]✅ Arquivo carregado: {file_path}[/green]")
            self.console.print(f"[blue]📊 Total de registros: {len(df)}[/blue]")

            self.analysis_stats["total_logs_processed"] += len(df)

            return df

        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo {file_path}: {str(e)}")
            self.console.print(f"[red]❌ Erro ao carregar {file_path}: {str(e)}[/red]")
            return None

    def analyze_firewall_logs(self, df: pd.DataFrame) -> None:
        """
        Analisa logs de firewall

        Args:
            df: DataFrame com logs de firewall
        """
        if df is None or df.empty:
            return

        self.logger.info("Iniciando análise de logs de firewall")
        self.analysis_stats["firewall_logs"] = len(df)

        # Filtrar tentativas negadas
        denied_attempts = df[df["action"] == "DENY"]

        if denied_attempts.empty:
            self.console.print(
                "[yellow]⚠️ Nenhuma tentativa bloqueada encontrada[/yellow]"
            )
            return

        # Agrupar por IP de origem
        denied_by_ip = (
            denied_attempts.groupby("source_ip")
            .agg(
                {
                    "port": lambda x: list(x.unique()),
                    "protocol": lambda x: list(x.unique()),
                    "timestamp": "count",
                }
            )
            .sort_values("timestamp", ascending=False)
        )

        # Criar tabela de resultados
        table = Table(title="🛡️ Tentativas Bloqueadas pelo Firewall", box=box.HEAVY)
        table.add_column("IP de Origem", style="yellow bold", no_wrap=True)
        table.add_column("Tentativas Negadas", style="red bold", justify="center")
        table.add_column("Portas Alvo", style="cyan")
        table.add_column("Protocolos", style="blue")

        for ip, data in denied_by_ip.head(10).iterrows():
            # Formatar portas (limitar para não quebrar tabela)
            ports_str = ", ".join(map(str, sorted(data["port"])))
            if len(ports_str) > 25:
                ports_str = ports_str[:22] + "..."

            protocols_str = ", ".join(data["protocol"])

            table.add_row(ip, str(data["timestamp"]), ports_str, protocols_str)

        self.console.print(table)
        self.console.print()

    def analyze_auth_logs(self, df: pd.DataFrame) -> None:
        """
        Analisa logs de autenticação

        Args:
            df: DataFrame com logs de autenticação
        """
        if df is None or df.empty:
            return

        self.logger.info("Iniciando análise de logs de autenticação")
        self.analysis_stats["auth_logs"] = len(df)

        # Filtrar tentativas falhadas (usar 'action' se não existir 'status')
        status_col = "status" if "status" in df.columns else "action"
        failed_attempts = df[df[status_col].isin(["FAIL", "FAILED"])]

        if failed_attempts.empty:
            self.console.print(
                "[green]✅ Nenhuma tentativa de login falhada encontrada[/green]"
            )
            return

        self.failed_logins = failed_attempts.to_dict("records")

        # Agrupar por IP
        failed_by_ip = (
            failed_attempts.groupby("source_ip")
            .agg(
                {
                    "username": lambda x: list(x.unique()),
                    "service": lambda x: list(x.unique()),
                    "timestamp": "count",
                }
            )
            .sort_values("timestamp", ascending=False)
        )

        # Criar tabela
        table = Table(title="🚫 Tentativas de Login Falhas por IP", box=box.HEAVY)
        table.add_column("IP de Origem", style="yellow bold", no_wrap=True)
        table.add_column("Tentativas", style="red bold", justify="center")
        table.add_column("Usuários Alvo", style="cyan")
        table.add_column("Serviços", style="blue")

        for ip, data in failed_by_ip.head(10).iterrows():
            users_str = ", ".join(data["username"][:3])
            if len(data["username"]) > 3:
                users_str += f"... (+{len(data['username']) - 3})"

            services_str = ", ".join(data["service"])

            table.add_row(ip, str(data["timestamp"]), users_str, services_str)

        self.console.print(table)
        self.console.print()

    def count_access_by_ip(
        self, df_firewall: Optional[pd.DataFrame], df_auth: Optional[pd.DataFrame]
    ) -> None:
        """
        Conta acessos totais por IP

        Args:
            df_firewall: DataFrame com logs de firewall
            df_auth: DataFrame com logs de autenticação
        """
        self.logger.info("Contando acessos por IP")

        # Contar acessos de firewall
        if df_firewall is not None and not df_firewall.empty:
            for ip in df_firewall["source_ip"]:
                if ip:  # Verificar se IP não está vazio
                    self.ip_access_count[ip] += 1

        # Contar acessos de autenticação
        if df_auth is not None and not df_auth.empty:
            for ip in df_auth["source_ip"]:
                if ip:  # Verificar se IP não está vazio
                    self.ip_access_count[ip] += 1

        if not self.ip_access_count:
            self.console.print(
                "[yellow]⚠️ Nenhum acesso encontrado para contabilizar[/yellow]"
            )
            return

        # Criar tabela de ranking
        table = Table(title="📊 Top IPs por Número de Acessos", box=box.HEAVY)
        table.add_column("IP de Origem", style="yellow bold", no_wrap=True)
        table.add_column("Total de Acessos", style="bold blue", justify="center")
        table.add_column("Classificação", style="bold", justify="center")

        config = self.config["risk_classification"]

        for ip, count in self.ip_access_count.most_common(15):
            # Classificação de risco
            if count >= config["high_threshold"]:
                risk_class = "🔴 Alto Risco"
            elif count >= config["medium_threshold"]:
                risk_class = "🟡 Médio Risco"
            else:
                risk_class = "🟢 Baixo Risco"

            table.add_row(ip, str(count), risk_class)

        self.console.print(table)
        self.console.print()

        # Atualizar estatísticas
        self.analysis_stats["suspect_ips_found"] = sum(
            1
            for count in self.ip_access_count.values()
            if count >= config["medium_threshold"]
        )

    def detect_brute_force(
        self,
        df: pd.DataFrame,
        time_window_minutes: Optional[int] = None,
        threshold: Optional[int] = None,
    ) -> None:
        """
        Detecta ataques de força bruta

        Args:
            df: DataFrame com logs de autenticação
            time_window_minutes: Janela de tempo em minutos
            threshold: Número mínimo de tentativas
        """
        if df is None or df.empty:
            return

        config = self.config["brute_force"]
        time_window = time_window_minutes or config["threshold"]
        min_attempts = threshold or config["time_window_minutes"]

        self.logger.info(
            f"Detectando brute force: {min_attempts}+ tentativas em {time_window} min"
        )

        # Filtrar tentativas falhadas (usar 'action' se não existir 'status')
        status_col = "status" if "status" in df.columns else "action"
        failed_attempts = df[df[status_col].isin(["FAIL", "FAILED"])].copy()

        if failed_attempts.empty:
            self.console.print(
                "[green]✅ Nenhuma tentativa falhada para análise[/green]"
            )
            return

        # Converter timestamps
        failed_attempts["timestamp"] = pd.to_datetime(failed_attempts["timestamp"])
        failed_attempts = failed_attempts.sort_values("timestamp")

        brute_force_detected = []

        # Analisar por IP
        for ip in failed_attempts["source_ip"].unique():
            ip_attempts = failed_attempts[failed_attempts["source_ip"] == ip]

            if len(ip_attempts) < min_attempts:
                continue

            # Verificar janelas de tempo
            for i in range(len(ip_attempts) - min_attempts + 1):
                window_start = ip_attempts.iloc[i]["timestamp"]
                window_end = window_start + timedelta(minutes=time_window)

                window_attempts = ip_attempts[
                    (ip_attempts["timestamp"] >= window_start)
                    & (ip_attempts["timestamp"] <= window_end)
                ]

                if len(window_attempts) >= min_attempts:
                    # Brute force detectado
                    attack_info = {
                        "ip": ip,
                        "start_time": window_start,
                        "end_time": window_attempts["timestamp"].max(),
                        "attempts": len(window_attempts),
                        "duration": (
                            window_attempts["timestamp"].max() - window_start
                        ).total_seconds(),
                        "users_targeted": list(window_attempts["username"].unique()),
                        "services": list(window_attempts["service"].unique()),
                    }
                    brute_force_detected.append(attack_info)
                    break  # Evitar duplicatas para o mesmo IP

        if not brute_force_detected:
            self.console.print(
                "[green]✅ Nenhum ataque de brute force detectado[/green]"
            )
            return

        # Armazenar resultados
        self.brute_force_attempts = brute_force_detected

        # Mostrar resultados
        self.console.print(
            Panel.fit(
                "[bold red]🚨 ATAQUES DE BRUTE FORCE DETECTADOS![/bold red]",
                border_style="red",
            )
        )

        table = Table(title="⚠️ Possíveis Ataques de Brute Force", box=box.HEAVY_EDGE)
        table.add_column("IP Atacante", style="yellow bold", no_wrap=True)
        table.add_column("Início do Ataque", style="cyan")
        table.add_column("Tentativas", style="red bold", justify="center")
        table.add_column("Usuários Alvo", style="bold blue")
        table.add_column("Serviços", style="white")
        table.add_column("Duração (s)", style="green", justify="center")

        for attack in brute_force_detected:
            users_text = ", ".join(attack["users_targeted"][:3])
            if len(attack["users_targeted"]) > 3:
                users_text += f"... (+{len(attack['users_targeted'])-3})"

            table.add_row(
                attack["ip"],
                attack["start_time"].strftime("%H:%M:%S"),
                str(attack["attempts"]),
                users_text,
                ", ".join(attack["services"]),
                f"{attack['duration']:.0f}",
            )

        self.console.print(table)
        self.console.print()

    def detect_port_scanning(
        self,
        df: pd.DataFrame,
        time_window_minutes: Optional[int] = None,
        min_ports: Optional[int] = None,
    ) -> None:
        """
        Detecta varreduras de portas

        Args:
            df: DataFrame com logs de firewall
            time_window_minutes: Janela de tempo em minutos
            min_ports: Número mínimo de portas
        """
        if df is None or df.empty:
            return

        config = self.config["port_scan"]
        time_window = time_window_minutes or config["time_window_minutes"]
        threshold = min_ports or config["threshold"]

        self.logger.info(
            f"Detectando port scanning: {threshold}+ portas em {time_window} min"
        )

        # Filtrar tentativas negadas (mais indicativo de scanning)
        denied_attempts = df[df["action"] == "DENY"].copy()

        if denied_attempts.empty:
            self.console.print(
                "[green]✅ Nenhuma tentativa negada para análise[/green]"
            )
            return

        # Converter timestamps
        denied_attempts["timestamp"] = pd.to_datetime(denied_attempts["timestamp"])
        denied_attempts = denied_attempts.sort_values("timestamp")

        port_scan_detected = []

        # Analisar por IP
        for ip in denied_attempts["source_ip"].unique():
            ip_attempts = denied_attempts[denied_attempts["source_ip"] == ip]

            # Contar portas únicas
            unique_ports = ip_attempts["port"].nunique()
            if unique_ports < threshold:
                continue

            # Analisar janelas de tempo
            start_time = ip_attempts["timestamp"].min()
            end_time = ip_attempts["timestamp"].max()
            duration = (end_time - start_time).total_seconds()

            # Se a duração for menor que a janela, considerar como port scan
            if duration <= (time_window * 60):
                scan_info = {
                    "ip": ip,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "unique_ports": unique_ports,
                    "ports_scanned": sorted(ip_attempts["port"].unique().tolist()),
                    "total_attempts": len(ip_attempts),
                    "target_hosts": list(ip_attempts["destination_ip"].unique()),
                    "protocols": list(ip_attempts["protocol"].unique()),
                    "scan_rate": (unique_ports / duration * 60) if duration > 0 else 0,
                    "actions": ip_attempts["action"].value_counts().to_dict(),
                }
                port_scan_detected.append(scan_info)

        if not port_scan_detected:
            self.console.print(
                "[green]✅ Nenhuma varredura de portas detectada[/green]"
            )
            return

        # Armazenar resultados
        self.port_scan_attempts = port_scan_detected

        # Mostrar resultados
        self.console.print(
            Panel.fit(
                "[bold yellow]🔍 VARREDURAS DE PORTAS DETECTADAS![/bold yellow]",
                border_style="yellow",
            )
        )

        table = Table(title="⚠️ Possíveis Port Scans", box=box.HEAVY)
        table.add_column("IP Atacante", style="yellow bold", no_wrap=True)
        table.add_column("Início", style="cyan")
        table.add_column("Portas", style="bold yellow", justify="center")
        table.add_column("Tentativas", style="red", justify="center")
        table.add_column("Taxa/min", style="magenta", justify="center")
        table.add_column("Alvos", style="white")
        table.add_column("Duração (s)", style="green", justify="center")

        for scan in port_scan_detected:
            actions = scan["actions"]
            allowed = actions.get("ALLOW", 0)
            denied = actions.get("DENY", 0)
            actions_text = f"✅{allowed} 🚫{denied}" if allowed > 0 else f"🚫{denied}"

            targets_text = ", ".join(scan["target_hosts"][:2])
            if len(scan["target_hosts"]) > 2:
                targets_text += f"... (+{len(scan['target_hosts'])-2})"

            table.add_row(
                scan["ip"],
                scan["start_time"].strftime("%H:%M:%S"),
                str(scan["unique_ports"]),
                f"{scan['total_attempts']} ({actions_text})",
                f"{scan['scan_rate']:.1f}",
                targets_text,
                f"{scan['duration']:.0f}",
            )

        self.console.print(table)
        self.console.print()

        # Mostrar detalhes das varreduras mais suspeitas
        for scan in sorted(
            port_scan_detected, key=lambda x: x["unique_ports"], reverse=True
        )[:3]:
            details = Text()
            details.append(f"🎯 IP: {scan['ip']}\n", style="bold yellow")
            details.append(
                f"⏰ Período: {scan['start_time'].strftime('%H:%M:%S')} ", style="cyan"
            )
            details.append(f"({format_duration(scan['duration'])})\n", style="cyan")
            details.append(f"🔢 Portas escaneadas: ", style="white")

            ports_sample = scan["ports_scanned"][:10]
            if len(scan["ports_scanned"]) > 10:
                details.append(
                    f"{', '.join(map(str, ports_sample))}... (+{len(scan['ports_scanned'])-10} mais)\n",
                    style="yellow",
                )
            else:
                details.append(f"{', '.join(map(str, ports_sample))}\n", style="yellow")

            details.append(
                f"🎯 Alvos: {', '.join(scan['target_hosts'])}\n", style="white"
            )
            details.append(
                f"📊 Protocolos: {', '.join(scan['protocols'])}\n", style="white"
            )

            # Classificação de risco
            if scan["unique_ports"] > 20:
                risk_level = "🔴 ALTO"
            elif scan["unique_ports"] > 15:
                risk_level = "🟠 MÉDIO"
            else:
                risk_level = "🟡 BAIXO"

            details.append(f"⚠️ Nível de Risco: {risk_level}\n", style="bold white")

            panel = Panel(
                details,
                title=f"🔍 Detalhes do Port Scan - {scan['ip']}",
                border_style="yellow",
                expand=False,
            )

            self.console.print(panel)

    def _run_geographic_analysis(self, geo_analyzer):
        """
        Executa análise geográfica usando o GeographicAnalyzer

        Args:
            geo_analyzer: Instância do GeographicAnalyzer
        """
        # Coletar IPs suspeitos
        suspect_ips = set()

        # Adicionar IPs de ataques de brute force
        for attack in self.brute_force_attempts:
            if "ip" in attack:
                suspect_ips.add(attack["ip"])

        # Adicionar IPs de port scanning
        for scan in self.port_scan_attempts:
            if "ip" in scan:
                suspect_ips.add(scan["ip"])

        # Adicionar IPs com muitos acessos
        config = self.config["risk_classification"]
        for ip, count in self.ip_access_count.items():
            if count >= config["medium_threshold"]:
                suspect_ips.add(ip)

        # Executar análise geográfica
        geo_analyzer.analyze_geographic_patterns(suspect_ips)

    def export_suspect_ips_csv(self, output_file: str) -> None:
        """
        Exporta IPs suspeitos para arquivo CSV

        Args:
            output_file: Caminho para o arquivo de saída
        """
        import csv
        from datetime import datetime

        try:
            # Coletar dados de IPs suspeitos
            suspect_data = []

            # IPs de brute force
            for attack in self.brute_force_attempts:
                suspect_data.append(
                    {
                        "ip": attack["ip"],
                        "tipo_de_alerta": "Brute Force",
                        "ocorrencias": attack["attempts"],
                        "primeira_deteccao": attack["start_time"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "ultima_deteccao": attack["end_time"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "servicos_afetados": ", ".join(attack["services"]),
                        "usuarios_alvo": ", ".join(attack["users_targeted"][:5]),
                    }
                )

            # IPs de port scanning
            for scan in self.port_scan_attempts:
                suspect_data.append(
                    {
                        "ip": scan["ip"],
                        "tipo_de_alerta": "Port Scanning",
                        "ocorrencias": scan["total_attempts"],
                        "primeira_deteccao": scan["start_time"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "ultima_deteccao": scan["end_time"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "servicos_afetados": f"{scan['unique_ports']} portas",
                        "usuarios_alvo": ", ".join(scan["target_hosts"]),
                    }
                )

            # IPs com alto número de acessos
            config = self.config["risk_classification"]
            for ip, count in self.ip_access_count.most_common():
                if count >= config["high_threshold"]:
                    # Verificar se já não está na lista
                    if not any(item["ip"] == ip for item in suspect_data):
                        suspect_data.append(
                            {
                                "ip": ip,
                                "tipo_de_alerta": "Alto Volume",
                                "ocorrencias": count,
                                "primeira_deteccao": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "ultima_deteccao": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "servicos_afetados": "Múltiplos",
                                "usuarios_alvo": "N/A",
                            }
                        )

            if not suspect_data:
                self.console.print(
                    "[yellow]⚠️ Nenhum IP suspeito encontrado para exportar[/yellow]"
                )
                return

            # Escrever arquivo CSV
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "ip",
                    "tipo_de_alerta",
                    "ocorrencias",
                    "primeira_deteccao",
                    "ultima_deteccao",
                    "servicos_afetados",
                    "usuarios_alvo",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in suspect_data:
                    writer.writerow(row)

            # Mostrar confirmação
            export_text = Text()
            export_text.append("📄 EXPORTAÇÃO CONCLUÍDA\n\n", style="bold green")
            export_text.append(f"✅ Arquivo: {output_file}\n", style="cyan")
            export_text.append(
                f"📊 Total de IPs suspeitos: {len(suspect_data)}\n", style="yellow"
            )

            # Estatísticas por tipo
            alert_types = {}
            for item in suspect_data:
                alert_type = item["tipo_de_alerta"]
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1

            export_text.append("\n📈 Distribuição por tipo:\n", style="white")
            for alert_type, count in alert_types.items():
                export_text.append(f"   • {alert_type}: {count} IPs\n", style="blue")

            panel = Panel(
                export_text,
                title="💾 Exportação CSV",
                border_style="green",
                expand=False,
            )

            self.console.print(panel)

        except Exception as e:
            self.logger.error(f"Erro ao exportar CSV: {str(e)}")
            self.console.print(f"[red]❌ Erro ao exportar CSV: {e}[/red]")

    def generate_summary(self) -> None:
        """Gera um resumo geral da análise de segurança"""

        summary_text = Text()
        summary_text.append("📋 RESUMO DA ANÁLISE DE SEGURANÇA\n\n", style="bold blue")

        # Estatísticas gerais
        summary_text.append(
            f"📊 Total de logs processados: {self.analysis_stats['total_logs_processed']}\n",
            style="white",
        )

        if self.failed_logins:
            summary_text.append(
                f"🚫 Total de tentativas de login falhadas: {len(self.failed_logins)}\n",
                style="red",
            )

        if self.ip_access_count:
            top_ip = self.ip_access_count.most_common(1)[0]
            summary_text.append(
                f"📊 IP com mais acessos: {top_ip[0]} ({top_ip[1]} acessos)\n",
                style="yellow",
            )

        if self.brute_force_attempts:
            summary_text.append(
                f"🚨 Ataques de brute force detectados: {len(self.brute_force_attempts)}\n",
                style="bold red",
            )
        else:
            summary_text.append(
                "✅ Nenhum ataque de brute force detectado\n", style="green"
            )

        if self.port_scan_attempts:
            summary_text.append(
                f"🔍 Varreduras de portas detectadas: {len(self.port_scan_attempts)}\n",
                style="bold yellow",
            )
        else:
            summary_text.append(
                "✅ Nenhuma varredura de portas detectada\n", style="green"
            )

        # Recomendações de segurança
        summary_text.append("\n🔒 RECOMENDAÇÕES DE SEGURANÇA:\n", style="bold cyan")

        if self.brute_force_attempts:
            summary_text.append(
                "• Considere implementar rate limiting\n", style="white"
            )
            summary_text.append("• Bloqueie IPs suspeitos no firewall\n", style="white")
            summary_text.append(
                "• Implemente autenticação de dois fatores\n", style="white"
            )

        if self.port_scan_attempts:
            summary_text.append(
                "• Configure detecção de port scanning\n", style="white"
            )
            summary_text.append(
                "• Implemente blacklist automática para scanners\n", style="white"
            )
            summary_text.append(
                "• Configure honeypots para detectar reconnaissance\n", style="white"
            )

        if self.ip_access_count:
            high_risk_count = sum(
                1
                for count in self.ip_access_count.values()
                if count >= self.config["risk_classification"]["high_threshold"]
            )
            if high_risk_count > 0:
                summary_text.append(
                    f"• Monitore {high_risk_count} IPs de alto risco\n", style="white"
                )

        summary_text.append("• Mantenha logs de auditoria atualizados\n", style="white")
        summary_text.append(
            "• Revise periodicamente políticas de acesso\n", style="white"
        )

        # Mostrar tempo de análise se disponível
        if (
            self.analysis_stats["analysis_start_time"]
            and self.analysis_stats["analysis_end_time"]
        ):
            duration = (
                self.analysis_stats["analysis_end_time"]
                - self.analysis_stats["analysis_start_time"]
            )
            summary_text.append(
                f"\n⏱️ Tempo de análise: {duration.total_seconds():.2f} segundos\n",
                style="cyan",
            )

        panel = Panel(
            summary_text,
            title="🛡️ Relatório de Segurança",
            border_style="blue",
            expand=False,
        )

        self.console.print(panel)

    def _display_analysis_stats(self) -> None:
        """Exibe estatísticas detalhadas da análise"""

        stats_text = Text()
        stats_text.append("📈 ESTATÍSTICAS DETALHADAS\n\n", style="bold green")

        stats_text.append(
            f"📊 Logs de firewall processados: {self.analysis_stats['firewall_logs']}\n",
            style="white",
        )
        stats_text.append(
            f"🔐 Logs de autenticação processados: {self.analysis_stats['auth_logs']}\n",
            style="white",
        )
        stats_text.append(
            f"🎯 IPs suspeitos encontrados: {self.analysis_stats['suspect_ips_found']}\n",
            style="yellow",
        )
        stats_text.append(
            f"🌍 IPs analisados geograficamente: {len(self.ip_location_cache)}\n",
            style="blue",
        )

        if (
            self.analysis_stats["analysis_start_time"]
            and self.analysis_stats["analysis_end_time"]
        ):
            duration = (
                self.analysis_stats["analysis_end_time"]
                - self.analysis_stats["analysis_start_time"]
            )
            stats_text.append(
                f"⏱️ Duração total: {duration.total_seconds():.2f} segundos\n",
                style="green",
            )

        panel = Panel(
            stats_text,
            title="📈 Estatísticas da Análise",
            border_style="green",
            expand=False,
        )

    # Métodos para compatibilidade com testes
    def load_data(self, file_path: str) -> bool:
        """
        Carrega dados de um arquivo para análise

        Args:
            file_path: Caminho para o arquivo

        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            self.data = self.load_log_file(file_path)
            return self.data is not None
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            return False

    def analyze_brute_force(self) -> pd.DataFrame:
        """
        Analisa força bruta nos dados carregados

        Returns:
            DataFrame com tentativas de força bruta detectadas
        """
        if self.data is None or self.data.empty:
            return pd.DataFrame()

        # Usar o método interno de detecção
        self.detect_brute_force(self.data)

        # Converter resultados para DataFrame
        if self.brute_force_attempts:
            return pd.DataFrame(self.brute_force_attempts)

        return pd.DataFrame()

    def generate_statistics(self) -> dict:
        """
        Gera estatísticas dos dados carregados

        Returns:
            Dicionário com estatísticas
        """
        if self.data is None or self.data.empty:
            return {
                "total_events": 0,
                "unique_ips": 0,
                "date_range": None,
                "top_ips": [],
            }

        stats = {
            "total_events": len(self.data),
            "unique_ips": (
                self.data["source_ip"].nunique()
                if "source_ip" in self.data.columns
                else 0
            ),
            "date_range": None,
            "top_ips": [],
        }

        # Adicionar range de datas se disponível
        if "timestamp" in self.data.columns:
            timestamps = pd.to_datetime(self.data["timestamp"], errors="coerce")
            if not timestamps.empty:
                stats["date_range"] = {
                    "start": timestamps.min().strftime("%Y-%m-%d %H:%M:%S"),
                    "end": timestamps.max().strftime("%Y-%m-%d %H:%M:%S"),
                }

        # Top IPs
        if "source_ip" in self.data.columns:
            top_ips = self.data["source_ip"].value_counts().head(5)
            stats["top_ips"] = [
                {"ip": ip, "count": count} for ip, count in top_ips.items()
            ]

        return stats

    def export_results(self, output_file: str, data) -> bool:
        """
        Exporta resultados para arquivo

        Args:
            output_file: Caminho do arquivo de saída
            data: Dados para exportar

        Returns:
            True se exportado com sucesso, False caso contrário
        """
        try:
            output_path = Path(output_file)
            ensure_directory_exists(str(output_path.parent))

            if output_path.suffix.lower() == ".csv":
                if isinstance(data, pd.DataFrame):
                    data.to_csv(output_file, index=False)
                else:
                    # Converter dict para DataFrame
                    df = pd.DataFrame([data] if isinstance(data, dict) else data)
                    df.to_csv(output_file, index=False)
            elif output_path.suffix.lower() == ".json":
                with open(output_file, "w", encoding="utf-8") as f:
                    if isinstance(data, pd.DataFrame):
                        json.dump(
                            data.to_dict("records"),
                            f,
                            indent=2,
                            ensure_ascii=False,
                            default=str,
                        )
                    else:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            return True
        except Exception as e:
            self.logger.error(f"Erro ao exportar resultados: {e}")
            return False

        self.console.print(panel)
