#!/usr/bin/env python3
"""
Log Analyzer - Ferramenta para análise de logs de segurança

Este script analisa logs de firewall e autenticação para detectar:
- Tentativas de login falhas
- Contagem de acessos por IP
- Possíveis ataques de brute force
- Estatísticas de segurança

Autor: Security Team
Data: 2024-09-28
"""

import pandas as pd
import os
import json
import requests
import pycountry
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import argparse
from geopy.distance import geodesic

# Inicializar o console do Rich para saída formatada
console = Console()

class LogAnalyzer:
    """Classe principal para análise de logs de segurança"""
    
    def __init__(self):
        self.console = Console()
        self.failed_logins = []
        self.ip_access_count = Counter()
        self.brute_force_attempts = defaultdict(list)
        self.port_scan_attempts = []
        self.ip_location_cache = {}  # Cache para evitar requisições duplicadas
    
    def load_log_file(self, file_path):
        """
        Carrega um arquivo de logs (CSV ou JSON)
        
        Args:
            file_path (str): Caminho para o arquivo de log
            
        Returns:
            pd.DataFrame: DataFrame com os dados do log ou None se houver erro
        """
        try:
            if not os.path.exists(file_path):
                self.console.print(f"[red]❌ Arquivo não encontrado: {file_path}[/red]")
                return None
            
            # Verificar extensão do arquivo
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                # Carregar arquivo CSV
                df = pd.read_csv(file_path)
                self.console.print(f"[green]✅ Arquivo CSV carregado com sucesso: {file_path}[/green]")
                
            elif file_extension == '.json':
                # Carregar arquivo JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Converter JSON para DataFrame
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                else:
                    # Se for um objeto JSON único, converter para lista
                    df = pd.DataFrame([json_data])
                
                self.console.print(f"[green]✅ Arquivo JSON carregado com sucesso: {file_path}[/green]")
                
            else:
                self.console.print(f"[red]❌ Formato de arquivo não suportado: {file_extension}[/red]")
                self.console.print("[yellow]💡 Formatos suportados: .csv, .json[/yellow]")
                return None
            
            # Converter coluna timestamp para datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                self.console.print(f"[yellow]⚠️  Coluna 'timestamp' não encontrada no arquivo[/yellow]")
                return None
            
            self.console.print(f"[blue]📊 Total de registros: {len(df)}[/blue]")
            self.console.print(f"[cyan]📝 Formato detectado: {file_extension.upper()[1:]}[/cyan]")
            
            return df
            
        except json.JSONDecodeError as e:
            self.console.print(f"[red]❌ Erro ao decodificar JSON: {e}[/red]")
            return None
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao carregar arquivo: {e}[/red]")
            return None
    
    def analyze_auth_logs(self, df):
        """
        Analisa logs de autenticação para identificar falhas de login
        
        Args:
            df (pd.DataFrame): DataFrame com logs de autenticação
        """
        if df is None or df.empty:
            return
        
        # Filtrar apenas tentativas de login falhas
        failed_attempts = df[df['action'] == 'FAILED'].copy()
        
        if failed_attempts.empty:
            self.console.print("[green]✅ Nenhuma tentativa de login falhada encontrada![/green]")
            return
        
        # Armazenar tentativas falhas para análise posterior
        self.failed_logins = failed_attempts.to_dict('records')
        
        # Contar falhas por IP
        failed_by_ip = failed_attempts.groupby('source_ip').size().sort_values(ascending=False)
        
        # Criar tabela de tentativas falhas por IP
        table = Table(title="🚫 Tentativas de Login Falhas por IP", box=box.ROUNDED)
        table.add_column("IP de Origem", style="red", no_wrap=True)
        table.add_column("Tentativas", style="bold red", justify="center")
        table.add_column("Usuários Alvo", style="yellow")
        table.add_column("Serviços", style="cyan")
        
        for ip, count in failed_by_ip.head(10).items():
            ip_attempts = failed_attempts[failed_attempts['source_ip'] == ip]
            users = ', '.join(ip_attempts['username'].unique())
            services = ', '.join(ip_attempts['service'].unique())
            
            table.add_row(
                ip,
                str(count),
                users[:30] + "..." if len(users) > 30 else users,
                services
            )
        
        self.console.print(table)
        self.console.print()
    
    def count_access_by_ip(self, df_firewall=None, df_auth=None):
        """
        Conta acessos por IP de origem de ambos os tipos de log
        
        Args:
            df_firewall (pd.DataFrame): DataFrame com logs de firewall
            df_auth (pd.DataFrame): DataFrame com logs de autenticação
        """
        ip_counts = Counter()
        
        # Contar IPs dos logs de firewall
        if df_firewall is not None and not df_firewall.empty:
            firewall_ips = df_firewall['source_ip'].value_counts()
            for ip, count in firewall_ips.items():
                ip_counts[ip] += count
        
        # Contar IPs dos logs de autenticação
        if df_auth is not None and not df_auth.empty:
            auth_ips = df_auth['source_ip'].value_counts()
            for ip, count in auth_ips.items():
                ip_counts[ip] += count
        
        if not ip_counts:
            self.console.print("[yellow]⚠️  Nenhum acesso encontrado nos logs[/yellow]")
            return
        
        # Criar tabela de contagem de acessos
        table = Table(title="📊 Top IPs por Número de Acessos", box=box.ROUNDED)
        table.add_column("IP de Origem", style="blue", no_wrap=True)
        table.add_column("Total de Acessos", style="bold green", justify="center")
        table.add_column("Classificação", style="yellow")
        
        # Classificar IPs por risco (baseado no número de acessos)
        for ip, count in ip_counts.most_common(15):
            if count > 10:
                classification = "🔴 Alto Risco"
            elif count > 5:
                classification = "🟡 Médio Risco"
            else:
                classification = "🟢 Baixo Risco"
            
            table.add_row(ip, str(count), classification)
        
        self.console.print(table)
        self.console.print()
        
        # Armazenar para uso posterior
        self.ip_access_count = ip_counts
    
    def detect_brute_force(self, df_auth, time_window_minutes=1, min_attempts=5):
        """
        Detecta possíveis ataques de brute force baseado em tentativas falhadas
        
        Args:
            df_auth (pd.DataFrame): DataFrame com logs de autenticação
            time_window_minutes (int): Janela de tempo em minutos para considerar
            min_attempts (int): Número mínimo de tentativas para considerar brute force
        """
        if df_auth is None or df_auth.empty:
            return
        
        # Filtrar apenas tentativas falhas
        failed_attempts = df_auth[df_auth['action'] == 'FAILED'].copy()
        
        if failed_attempts.empty:
            self.console.print("[green]✅ Nenhuma tentativa de brute force detectada![/green]")
            return
        
        # Agrupar por IP e analisar tentativas em janela de tempo
        brute_force_detected = []
        
        for ip in failed_attempts['source_ip'].unique():
            ip_attempts = failed_attempts[failed_attempts['source_ip'] == ip].sort_values('timestamp')
            
            # Verificar tentativas em janela de tempo
            for i, attempt in ip_attempts.iterrows():
                time_start = attempt['timestamp']
                time_end = time_start + timedelta(minutes=time_window_minutes)
                
                # Contar tentativas na janela de tempo
                window_attempts = ip_attempts[
                    (ip_attempts['timestamp'] >= time_start) & 
                    (ip_attempts['timestamp'] <= time_end)
                ]
                
                if len(window_attempts) >= min_attempts:
                    brute_force_detected.append({
                        'ip': ip,
                        'start_time': time_start,
                        'attempts': len(window_attempts),
                        'users_targeted': window_attempts['username'].unique().tolist(),
                        'services': window_attempts['service'].unique().tolist(),
                        'duration': (window_attempts['timestamp'].max() - 
                                   window_attempts['timestamp'].min()).total_seconds()
                    })
                    break  # Evitar duplicatas para o mesmo IP
        
        if not brute_force_detected:
            self.console.print(f"[green]✅ Nenhum ataque de brute force detectado![/green]")
            self.console.print(f"[blue]ℹ️  Critérios: {min_attempts}+ tentativas em {time_window_minutes} minuto(s)[/blue]")
            return
        
        # Exibir ataques detectados
        self.console.print(Panel.fit(
            f"🚨 [bold red]ATAQUES DE BRUTE FORCE DETECTADOS![/bold red]",
            border_style="red"
        ))
        
        table = Table(title="⚠️  Possíveis Ataques de Brute Force", box=box.HEAVY)
        table.add_column("IP Atacante", style="red bold", no_wrap=True)
        table.add_column("Início do Ataque", style="yellow")
        table.add_column("Tentativas", style="bold red", justify="center")
        table.add_column("Usuários Alvo", style="cyan")
        table.add_column("Serviços", style="magenta")
        table.add_column("Duração (s)", style="white", justify="center")
        
        for attack in brute_force_detected:
            table.add_row(
                attack['ip'],
                attack['start_time'].strftime('%H:%M:%S'),
                str(attack['attempts']),
                ', '.join(attack['users_targeted'][:3]) + 
                ("..." if len(attack['users_targeted']) > 3 else ""),
                ', '.join(attack['services']),
                f"{attack['duration']:.0f}"
            )
        
        self.console.print(table)
        self.console.print()
        
        # Armazenar para relatório
        self.brute_force_attempts = brute_force_detected
    
    def detect_port_scanning(self, df_firewall, time_window_minutes=1, min_ports=10):
        """
        Detecta possíveis varreduras de portas baseado em tentativas de acesso a múltiplas portas
        
        Args:
            df_firewall (pd.DataFrame): DataFrame com logs de firewall
            time_window_minutes (int): Janela de tempo em minutos para considerar
            min_ports (int): Número mínimo de portas para considerar port scanning
        """
        if df_firewall is None or df_firewall.empty:
            return
        
        # Analisar todas as tentativas (ALLOW e DENY)
        port_scan_detected = []
        
        # Agrupar por IP e analisar tentativas de acesso a portas diferentes
        for ip in df_firewall['source_ip'].unique():
            ip_attempts = df_firewall[df_firewall['source_ip'] == ip].sort_values('timestamp')
            
            # Verificar tentativas em janela de tempo
            for i, attempt in ip_attempts.iterrows():
                time_start = attempt['timestamp']
                time_end = time_start + timedelta(minutes=time_window_minutes)
                
                # Buscar tentativas na janela de tempo
                window_attempts = ip_attempts[
                    (ip_attempts['timestamp'] >= time_start) & 
                    (ip_attempts['timestamp'] <= time_end)
                ]
                
                # Contar portas únicas acessadas
                unique_ports = window_attempts['port'].nunique()
                
                if unique_ports >= min_ports:
                    # Análise adicional dos dados
                    ports_list = sorted(window_attempts['port'].unique())
                    protocols = window_attempts['protocol'].unique().tolist()
                    actions = window_attempts['action'].value_counts().to_dict()
                    destinations = window_attempts['destination_ip'].unique().tolist()
                    
                    port_scan_detected.append({
                        'ip': ip,
                        'start_time': time_start,
                        'unique_ports': unique_ports,
                        'total_attempts': len(window_attempts),
                        'ports_scanned': ports_list,
                        'protocols': protocols,
                        'actions': actions,
                        'target_hosts': destinations,
                        'duration': (window_attempts['timestamp'].max() - 
                                   window_attempts['timestamp'].min()).total_seconds(),
                        'scan_rate': unique_ports / max(1, (window_attempts['timestamp'].max() - 
                                                          window_attempts['timestamp'].min()).total_seconds()) * 60
                    })
                    break  # Evitar duplicatas para o mesmo IP
        
        if not port_scan_detected:
            self.console.print(f"[green]✅ Nenhuma varredura de portas detectada![/green]")
            self.console.print(f"[blue]ℹ️  Critérios: {min_ports}+ portas em {time_window_minutes} minuto(s)[/blue]")
            return
        
        # Exibir varreduras detectadas
        self.console.print(Panel.fit(
            f"🔍 [bold yellow]VARREDURAS DE PORTAS DETECTADAS![/bold yellow]",
            border_style="yellow"
        ))
        
        table = Table(title="⚠️  Possíveis Port Scans", box=box.HEAVY)
        table.add_column("IP Atacante", style="yellow bold", no_wrap=True)
        table.add_column("Início", style="cyan")
        table.add_column("Portas", style="bold yellow", justify="center")
        table.add_column("Tentativas", style="red", justify="center")
        table.add_column("Taxa/min", style="magenta", justify="center")
        table.add_column("Alvos", style="white")
        table.add_column("Duração (s)", style="green", justify="center")
        
        for scan in port_scan_detected:
            # Calcular estatísticas
            allowed = scan['actions'].get('ALLOW', 0)
            denied = scan['actions'].get('DENY', 0)
            
            # Formato das ações
            actions_text = f"✅{allowed} 🚫{denied}" if allowed > 0 else f"🚫{denied}"
            
            # Alvos (limitar para não quebrar tabela)
            targets_text = ', '.join(scan['target_hosts'][:2])
            if len(scan['target_hosts']) > 2:
                targets_text += f"... (+{len(scan['target_hosts'])-2})"
            
            table.add_row(
                scan['ip'],
                scan['start_time'].strftime('%H:%M:%S'),
                str(scan['unique_ports']),
                f"{scan['total_attempts']} ({actions_text})",
                f"{scan['scan_rate']:.1f}",
                targets_text,
                f"{scan['duration']:.0f}"
            )
        
        self.console.print(table)
        self.console.print()
        
        # Mostrar detalhes das varreduras mais suspeitas
        suspicious_scans = sorted(port_scan_detected, key=lambda x: x['unique_ports'], reverse=True)[:3]
        
        for scan in suspicious_scans:
            # Criar painel de detalhes
            details = Text()
            details.append(f"🎯 IP: {scan['ip']}\n", style="bold yellow")
            details.append(f"⏰ Período: {scan['start_time'].strftime('%H:%M:%S')} ", style="cyan")
            details.append(f"({scan['duration']:.0f}s)\n", style="cyan")
            details.append(f"🔢 Portas escaneadas: ", style="white")
            
            # Mostrar algumas portas como exemplo
            ports_sample = scan['ports_scanned'][:10]
            if len(scan['ports_scanned']) > 10:
                details.append(f"{', '.join(map(str, ports_sample))}... (+{len(scan['ports_scanned'])-10} mais)\n", style="yellow")
            else:
                details.append(f"{', '.join(map(str, ports_sample))}\n", style="yellow")
            
            details.append(f"🎯 Alvos: {', '.join(scan['target_hosts'])}\n", style="white")
            details.append(f"📊 Protocolos: {', '.join(scan['protocols'])}\n", style="blue")
            
            # Análise de risco
            risk_level = "🔴 ALTO" if scan['unique_ports'] > 50 else "🟡 MÉDIO" if scan['unique_ports'] > 25 else "🟠 BAIXO"
            details.append(f"⚠️  Nível de Risco: {risk_level}", style="bold red" if "ALTO" in risk_level else "bold yellow")
            
            panel = Panel(
                details,
                title=f"🔍 Detalhes do Port Scan - {scan['ip']}",
                border_style="yellow",
                expand=False
            )
            
            self.console.print(panel)
        
        # Armazenar para relatório
        self.port_scan_attempts = port_scan_detected
    
    def export_suspect_ips_csv(self, output_file="suspect_ips.csv"):
        """
        Exporta IPs suspeitos para arquivo CSV
        
        Args:
            output_file (str): Nome do arquivo CSV de saída
        """
        try:
            import csv
            
            # Coletar todos os IPs suspeitos com seus alertas
            suspect_data = []
            
            # IPs com tentativas de login falhas
            if self.failed_logins:
                failed_by_ip = {}
                for attempt in self.failed_logins:
                    ip = attempt['source_ip']
                    failed_by_ip[ip] = failed_by_ip.get(ip, 0) + 1
                
                for ip, count in failed_by_ip.items():
                    suspect_data.append({
                        'ip': ip,
                        'tipo_de_alerta': 'LOGIN_FALHA',
                        'quantidade_de_ocorrencias': count
                    })
            
            # IPs com ataques de brute force
            if hasattr(self, 'brute_force_attempts') and self.brute_force_attempts:
                for attack in self.brute_force_attempts:
                    suspect_data.append({
                        'ip': attack['ip'],
                        'tipo_de_alerta': 'BRUTE_FORCE',
                        'quantidade_de_ocorrencias': attack['attempts']
                    })
            
            # IPs com varreduras de portas
            if hasattr(self, 'port_scan_attempts') and self.port_scan_attempts:
                for scan in self.port_scan_attempts:
                    suspect_data.append({
                        'ip': scan['ip'],
                        'tipo_de_alerta': 'PORT_SCAN',
                        'quantidade_de_ocorrencias': scan['unique_ports']
                    })
            
            # IPs de alto risco (baseado no número de acessos)
            if self.ip_access_count:
                high_risk_ips = {ip: count for ip, count in self.ip_access_count.items() if count > 10}
                for ip, count in high_risk_ips.items():
                    # Verificar se já não foi adicionado com outro tipo de alerta
                    existing_ips = [item['ip'] for item in suspect_data]
                    if ip not in existing_ips:
                        suspect_data.append({
                            'ip': ip,
                            'tipo_de_alerta': 'ALTO_RISCO',
                            'quantidade_de_ocorrencias': count
                        })
            
            if not suspect_data:
                self.console.print("[green]✅ Nenhum IP suspeito encontrado para exportar![/green]")
                return
            
            # Escrever arquivo CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ip', 'tipo_de_alerta', 'quantidade_de_ocorrencias']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Escrever cabeçalho
                writer.writeheader()
                
                # Escrever dados
                for row in suspect_data:
                    writer.writerow(row)
            
            # Criar painel de confirmação
            export_text = Text()
            export_text.append("📄 EXPORTAÇÃO CONCLUÍDA\n\n", style="bold green")
            export_text.append(f"✅ Arquivo: {output_file}\n", style="cyan")
            export_text.append(f"📊 Total de IPs suspeitos: {len(suspect_data)}\n", style="yellow")
            
            # Estatísticas por tipo
            alert_types = {}
            for item in suspect_data:
                alert_type = item['tipo_de_alerta']
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            
            export_text.append("\n📈 Distribuição por tipo:\n", style="white")
            for alert_type, count in alert_types.items():
                export_text.append(f"   • {alert_type}: {count} IPs\n", style="blue")
            
            panel = Panel(
                export_text,
                title="💾 Exportação CSV",
                border_style="green",
                expand=False
            )
            
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao exportar CSV: {e}[/red]")
    
    def get_ip_location(self, ip_address):
        """
        Obtém informações de geolocalização para um endereço IP
        
        Args:
            ip_address (str): Endereço IP para consulta
            
        Returns:
            dict: Informações de localização ou None se houver erro
        """
        # Verificar se já está no cache
        if ip_address in self.ip_location_cache:
            return self.ip_location_cache[ip_address]
        
        try:
            # Usar IP-API (gratuito, sem necessidade de API key)
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,lat,lon,isp,org,as",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    location_info = {
                        'country': data.get('country', 'Desconhecido'),
                        'country_code': data.get('countryCode', 'XX'),
                        'region': data.get('regionName', 'Desconhecido'),
                        'city': data.get('city', 'Desconhecido'),
                        'latitude': data.get('lat', 0),
                        'longitude': data.get('lon', 0),
                        'isp': data.get('isp', 'Desconhecido'),
                        'organization': data.get('org', 'Desconhecido'),
                        'as_info': data.get('as', 'Desconhecido')
                    }
                    
                    # Adicionar ao cache
                    self.ip_location_cache[ip_address] = location_info
                    return location_info
                else:
                    self.console.print(f"[yellow]⚠️  Não foi possível obter localização para {ip_address}: {data.get('message', 'Erro desconhecido')}[/yellow]")
            
            # Rate limiting (IP-API permite 45 req/min para uso gratuito)
            time.sleep(1.5)
            
        except requests.exceptions.Timeout:
            self.console.print(f"[yellow]⚠️  Timeout ao consultar localização do IP {ip_address}[/yellow]")
        except requests.exceptions.RequestException as e:
            self.console.print(f"[yellow]⚠️  Erro na requisição de geolocalização para {ip_address}: {e}[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Erro inesperado na geolocalização de {ip_address}: {e}[/red]")
        
        return None
    
    def analyze_geographic_patterns(self, df):
        """
        Analisa padrões geográficos nos logs para detectar anomalias
        
        Args:
            df (pd.DataFrame): DataFrame com logs para análise
        """
        if df is None or df.empty:
            return
        
        self.console.print("\n🌍 ANÁLISE GEOGRÁFICA\n", style="bold blue")
        
        # Obter IPs suspeitos únicos
        suspect_ips = set()
        
        # Adicionar IPs de ataques de brute force
        if hasattr(self, 'brute_force_attempts') and self.brute_force_attempts:
            if isinstance(self.brute_force_attempts, list):
                # brute_force_attempts é uma lista de dicionários
                for attack in self.brute_force_attempts:
                    if 'ip' in attack:
                        suspect_ips.add(attack['ip'])
            elif isinstance(self.brute_force_attempts, dict):
                # brute_force_attempts é um dicionário
                for ip in self.brute_force_attempts.keys():
                    suspect_ips.add(ip)
        
        # Adicionar IPs de port scanning
        if hasattr(self, 'port_scan_attempts') and self.port_scan_attempts:
            for scan in self.port_scan_attempts:
                if 'ip' in scan:
                    suspect_ips.add(scan['ip'])
        
        # Adicionar IPs com muitos acessos negados
        if 'action' in df.columns:
            denied_attempts = df[df['action'] == 'DENY']
            if not denied_attempts.empty:
                top_denied = denied_attempts.groupby('source_ip').size().sort_values(ascending=False).head(10)
                for ip in top_denied.index:
                    suspect_ips.add(ip)
        
        if not suspect_ips:
            self.console.print("[green]✅ Nenhum IP suspeito encontrado para análise geográfica[/green]")
            return
        
        self.console.print(f"🔍 Analisando {len(suspect_ips)} IPs suspeitos...\n")
        
        # Coletar informações geográficas
        geo_data = []
        countries_count = Counter()
        suspicious_countries = ['CN', 'RU', 'KP', 'IR']  # Países frequentemente associados a ataques
        
        for ip in suspect_ips:
            location = self.get_ip_location(ip)
            if location:
                geo_data.append({
                    'ip': ip,
                    'country': location['country'],
                    'country_code': location['country_code'],
                    'city': location['city'],
                    'region': location['region'],
                    'isp': location['isp'],
                    'organization': location['organization'],
                    'latitude': location['latitude'],
                    'longitude': location['longitude']
                })
                countries_count[location['country']] += 1
        
        if not geo_data:
            self.console.print("[yellow]⚠️  Não foi possível obter dados geográficos para os IPs suspeitos[/yellow]")
            return
        
        # Criar tabela de distribuição por país
        table = Table(title="🌎 Distribuição Geográfica dos IPs Suspeitos", box=box.HEAVY)
        table.add_column("País", style="cyan bold")
        table.add_column("Código", style="yellow", justify="center")
        table.add_column("Quantidade", style="red bold", justify="center")
        table.add_column("Percentual", style="green", justify="center")
        table.add_column("Status", style="white", justify="center")
        
        total_ips = len(geo_data)
        
        for country, count in countries_count.most_common():
            percentage = (count / total_ips) * 100
            
            # Encontrar código do país
            country_code = next((item['country_code'] for item in geo_data if item['country'] == country), 'XX')
            
            # Status de risco
            if country_code in suspicious_countries:
                status = "🚨 Alto Risco"
                status_style = "bold red"
            elif percentage > 30:
                status = "⚠️  Concentração Alta"
                status_style = "bold yellow"
            else:
                status = "✅ Normal"
                status_style = "green"
            
            table.add_row(
                country,
                country_code,
                str(count),
                f"{percentage:.1f}%",
                status
            )
        
        self.console.print(table)
        self.console.print()
        
        # Detectar anomalias geográficas
        self.detect_geographic_anomalies(geo_data, df)
    
    def detect_geographic_anomalies(self, geo_data, df):
        """
        Detecta anomalias geográficas como viagens impossíveis
        
        Args:
            geo_data (list): Lista com dados geográficos dos IPs
            df (pd.DataFrame): DataFrame com logs para análise temporal
        """
        self.console.print("🔍 DETECÇÃO DE ANOMALIAS GEOGRÁFICAS\n", style="bold yellow")
        
        # Analisar padrões temporais por IP (se disponível coluna de timestamp)
        timestamp_col = None
        for col in ['timestamp', 'date', 'time', 'datetime']:
            if col in df.columns:
                timestamp_col = col
                break
        
        if not timestamp_col:
            self.console.print("[yellow]⚠️  Coluna de timestamp não encontrada. Análise de viagem impossível desabilitada.[/yellow]")
            return
        
        # Criar tabela de detalhes por IP
        table = Table(title="📍 Detalhes Geográficos dos IPs Suspeitos", box=box.ROUNDED)
        table.add_column("IP", style="yellow bold", no_wrap=True)
        table.add_column("País/Região", style="cyan")
        table.add_column("Cidade", style="white")
        table.add_column("ISP", style="blue")
        table.add_column("Coordenadas", style="green")
        table.add_column("Risco", style="red", justify="center")
        
        suspicious_countries = ['CN', 'RU', 'KP', 'IR', 'BY']
        
        for item in geo_data:
            # Determinar nível de risco
            risk_factors = []
            
            if item['country_code'] in suspicious_countries:
                risk_factors.append("País de Alto Risco")
            
            if 'proxy' in item['organization'].lower() or 'vpn' in item['organization'].lower():
                risk_factors.append("VPN/Proxy")
            
            if 'hosting' in item['isp'].lower() or 'server' in item['isp'].lower():
                risk_factors.append("Hosting/Server")
            
            # Nível de risco
            if len(risk_factors) >= 2:
                risk_level = "🚨 Alto"
                risk_style = "bold red"
            elif len(risk_factors) == 1:
                risk_level = "⚠️  Médio"
                risk_style = "yellow"
            else:
                risk_level = "✅ Baixo"
                risk_style = "green"
            
            coords = f"{item['latitude']:.2f}, {item['longitude']:.2f}"
            location = f"{item['country']}/{item['region']}"
            
            table.add_row(
                item['ip'],
                location,
                item['city'],
                item['isp'][:30] + "..." if len(item['isp']) > 30 else item['isp'],
                coords,
                risk_level
            )
        
        self.console.print(table)
        self.console.print()
        
        # Sugestões baseadas na análise geográfica
        suggestions = Text()
        suggestions.append("💡 RECOMENDAÇÕES BASEADAS NA ANÁLISE GEOGRÁFICA:\n\n", style="bold cyan")
        
        high_risk_countries = [item for item in geo_data if item['country_code'] in suspicious_countries]
        if high_risk_countries:
            suggestions.append("🚨 IPs de países de alto risco detectados:\n", style="bold red")
            for item in high_risk_countries[:5]:  # Mostrar apenas os primeiros 5
                suggestions.append(f"   • {item['ip']} ({item['country']})\n", style="red")
            suggestions.append("\n")
        
        proxy_ips = [item for item in geo_data if 'proxy' in item['organization'].lower() or 'vpn' in item['organization'].lower()]
        if proxy_ips:
            suggestions.append("🔒 IPs usando VPN/Proxy detectados:\n", style="bold yellow")
            for item in proxy_ips[:3]:
                suggestions.append(f"   • {item['ip']} - {item['organization']}\n", style="yellow")
            suggestions.append("\n")
        
        suggestions.append("🛡️  Ações recomendadas:\n", style="bold white")
        suggestions.append("   • Implementar geo-blocking para países de alto risco\n", style="white")
        suggestions.append("   • Monitorar conexões através de VPN/Proxy\n", style="white")
        suggestions.append("   • Configurar alertas para mudanças geográficas bruscas\n", style="white")
        suggestions.append("   • Considerar autenticação adicional para localizações incomuns\n", style="white")
        
        panel = Panel(
            suggestions,
            title="🌍 Análise Geográfica Concluída",
            border_style="cyan",
            expand=False
        )
        
        self.console.print(panel)
    
    def analyze_firewall_logs(self, df):
        """
        Analisa logs de firewall para identificar padrões suspeitos
        
        Args:
            df (pd.DataFrame): DataFrame com logs de firewall
        """
        if df is None or df.empty:
            return
        
        # Analisar ações negadas
        denied_attempts = df[df['action'] == 'DENY']
        
        if not denied_attempts.empty:
            # IPs com mais tentativas negadas
            denied_by_ip = denied_attempts.groupby('source_ip').size().sort_values(ascending=False)
            
            table = Table(title="🛡️  Tentativas Bloqueadas pelo Firewall", box=box.ROUNDED)
            table.add_column("IP de Origem", style="red", no_wrap=True)
            table.add_column("Tentativas Negadas", style="bold red", justify="center")
            table.add_column("Portas Alvo", style="yellow")
            table.add_column("Protocolos", style="cyan")
            
            for ip, count in denied_by_ip.head(10).items():
                ip_attempts = denied_attempts[denied_attempts['source_ip'] == ip]
                ports = ', '.join(map(str, sorted(ip_attempts['port'].unique())))
                protocols = ', '.join(ip_attempts['protocol'].unique())
                
                table.add_row(
                    ip,
                    str(count),
                    ports[:20] + "..." if len(ports) > 20 else ports,
                    protocols
                )
            
            self.console.print(table)
            self.console.print()
    
    def generate_summary(self):
        """Gera um resumo geral da análise de segurança"""
        
        summary_text = Text()
        summary_text.append("📋 RESUMO DA ANÁLISE DE SEGURANÇA\n\n", style="bold blue")
        
        # Estatísticas gerais
        if self.failed_logins:
            summary_text.append(f"🚫 Total de tentativas de login falhadas: {len(self.failed_logins)}\n", style="red")
        
        if self.ip_access_count:
            top_ip = self.ip_access_count.most_common(1)[0]
            summary_text.append(f"📊 IP com mais acessos: {top_ip[0]} ({top_ip[1]} acessos)\n", style="yellow")
        
        if self.brute_force_attempts:
            summary_text.append(f"🚨 Ataques de brute force detectados: {len(self.brute_force_attempts)}\n", style="bold red")
        else:
            summary_text.append("✅ Nenhum ataque de brute force detectado\n", style="green")
        
        if hasattr(self, 'port_scan_attempts') and self.port_scan_attempts:
            summary_text.append(f"🔍 Varreduras de portas detectadas: {len(self.port_scan_attempts)}\n", style="bold yellow")
        else:
            summary_text.append("✅ Nenhuma varredura de portas detectada\n", style="green")
        
        # Recomendações de segurança
        summary_text.append("\n🔒 RECOMENDAÇÕES DE SEGURANÇA:\n", style="bold cyan")
        
        if self.brute_force_attempts:
            summary_text.append("• Considere implementar rate limiting\n", style="white")
            summary_text.append("• Bloqueie IPs suspeitos no firewall\n", style="white")
            summary_text.append("• Implemente autenticação de dois fatores\n", style="white")
        
        if hasattr(self, 'port_scan_attempts') and self.port_scan_attempts:
            summary_text.append("• Configure detecção de port scanning\n", style="white")
            summary_text.append("• Implemente blacklist automática para scanners\n", style="white")
            summary_text.append("• Configure honeypots para detectar reconnaissance\n", style="white")
        
        if self.ip_access_count:
            high_risk_ips = [ip for ip, count in self.ip_access_count.items() if count > 10]
            if high_risk_ips:
                summary_text.append(f"• Monitore {len(high_risk_ips)} IPs de alto risco\n", style="white")
        
        summary_text.append("• Mantenha logs de auditoria atualizados\n", style="white")
        summary_text.append("• Revise periodicamente políticas de acesso\n", style="white")
        
        panel = Panel(
            summary_text,
            title="🛡️ Relatório de Segurança",
            border_style="green",
            expand=False
        )
        
        self.console.print(panel)

def main():
    """Função principal do programa"""
    parser = argparse.ArgumentParser(description='Analisador de Logs de Segurança')
    parser.add_argument('--firewall', type=str, help='Arquivo CSV/JSON com logs de firewall')
    parser.add_argument('--auth', type=str, help='Arquivo CSV/JSON com logs de autenticação')
    parser.add_argument('--samples', action='store_true', help='Usar arquivos de exemplo (CSV)')
    parser.add_argument('--samples-json', action='store_true', help='Usar arquivos de exemplo (JSON)')
    parser.add_argument('--brute-force-threshold', type=int, default=5, 
                       help='Número mínimo de tentativas para detectar brute force (padrão: 5)')
    parser.add_argument('--time-window', type=int, default=1,
                       help='Janela de tempo em minutos para detectar brute force (padrão: 1)')
    parser.add_argument('--port-scan-threshold', type=int, default=10,
                       help='Número mínimo de portas para detectar port scan (padrão: 10)')
    parser.add_argument('--port-scan-window', type=int, default=1,
                       help='Janela de tempo em minutos para detectar port scan (padrão: 1)')
    parser.add_argument('--export-csv', type=str, default=None,
                       help='Exportar IPs suspeitos para arquivo CSV (ex: suspect_ips.csv)')
    parser.add_argument('--auto-export', action='store_true',
                       help='Exportar automaticamente para suspect_ips.csv')
    parser.add_argument('--disable-geo', action='store_true',
                       help='Desabilitar análise geográfica (útil para melhor performance)')
    parser.add_argument('--geo-timeout', type=int, default=5,
                       help='Timeout para consultas de geolocalização em segundos (padrão: 5)')
    
    args = parser.parse_args()
    
    # Inicializar analisador
    analyzer = LogAnalyzer()
    
    # Exibir cabeçalho
    console.print(Panel.fit(
        "[bold blue]🔍 LOG ANALYZER - FERRAMENTA DE ANÁLISE DE SEGURANÇA[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    # Definir caminhos dos arquivos
    if args.samples:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        firewall_file = os.path.join(script_dir, 'samples', 'firewall_logs.csv')
        auth_file = os.path.join(script_dir, 'samples', 'auth_logs.csv')
    elif args.samples_json:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        firewall_file = os.path.join(script_dir, 'samples', 'firewall_logs.json')
        auth_file = os.path.join(script_dir, 'samples', 'auth_logs.json')
    else:
        firewall_file = args.firewall
        auth_file = args.auth
    
    # Carregar arquivos
    df_firewall = None
    df_auth = None
    
    if firewall_file:
        console.print(f"[blue]🔄 Carregando logs de firewall...[/blue]")
        df_firewall = analyzer.load_log_file(firewall_file)
    
    if auth_file:
        console.print(f"[blue]🔄 Carregando logs de autenticação...[/blue]")
        df_auth = analyzer.load_log_file(auth_file)
    
    if df_firewall is None and df_auth is None:
        console.print("[red]❌ Nenhum arquivo válido foi carregado![/red]")
        console.print("[yellow]💡 Use --samples para testar com dados CSV de exemplo[/yellow]")
        console.print("[yellow]💡 Use --samples-json para testar com dados JSON de exemplo[/yellow]")
        console.print("[yellow]💡 Ou especifique --firewall e/ou --auth com caminhos válidos[/yellow]")
        return
    
    console.print()
    
    # Executar análises
    console.print("[bold green]🔍 INICIANDO ANÁLISE DE SEGURANÇA...[/bold green]")
    console.print()
    
    # 1. Analisar logs de firewall
    if df_firewall is not None:
        console.print("[blue]📊 Analisando logs de firewall...[/blue]")
        analyzer.analyze_firewall_logs(df_firewall)
    
    # 2. Analisar tentativas de login falhas
    if df_auth is not None:
        console.print("[blue]🔐 Analisando tentativas de autenticação...[/blue]")
        analyzer.analyze_auth_logs(df_auth)
    
    # 3. Contar acessos por IP
    console.print("[blue]🌐 Contando acessos por IP...[/blue]")
    analyzer.count_access_by_ip(df_firewall, df_auth)
    
    # 4. Detectar ataques de brute force
    if df_auth is not None:
        console.print(f"[blue]⚡ Detectando ataques de brute force ({args.brute_force_threshold}+ tentativas em {args.time_window} min)...[/blue]")
        analyzer.detect_brute_force(df_auth, args.time_window, args.brute_force_threshold)
    
    # 5. Detectar varreduras de portas
    if df_firewall is not None:
        console.print(f"[blue]🔍 Detectando varreduras de portas ({args.port_scan_threshold}+ portas em {args.port_scan_window} min)...[/blue]")
        analyzer.detect_port_scanning(df_firewall, args.port_scan_window, args.port_scan_threshold)
    
    # 6. Análise Geográfica
    if not args.disable_geo and (df_firewall is not None or df_auth is not None):
        console.print("[blue]🌍 Executando análise geográfica dos IPs suspeitos...[/blue]")
        # Usar o DataFrame de firewall como principal, ou auth se firewall não estiver disponível
        primary_df = df_firewall if df_firewall is not None else df_auth
        analyzer.analyze_geographic_patterns(primary_df)
    elif args.disable_geo:
        console.print("[yellow]⏭️  Análise geográfica desabilitada pelo usuário[/yellow]")
    
    # 7. Gerar resumo final
    console.print("[bold green]📋 GERANDO RESUMO FINAL...[/bold green]")
    console.print()
    analyzer.generate_summary()
    
    # 8. Exportar resultados se solicitado
    if args.export_csv or args.auto_export:
        console.print()
        console.print("[bold blue]💾 EXPORTANDO RESULTADOS...[/bold blue]")
        console.print()
        
        if args.export_csv:
            output_file = args.export_csv
        else:
            output_file = "suspect_ips.csv"
        
        analyzer.export_suspect_ips_csv(output_file)
    
    console.print()
    console.print("[bold green]✅ Análise concluída com sucesso![/bold green]")

if __name__ == "__main__":
    main()