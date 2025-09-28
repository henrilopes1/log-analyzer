#!/usr/bin/env python3
"""
Log Analyzer - Ponto de entrada principal
==========================================

Ferramenta para análise de logs de segurança com detecção de:
- Tentativas de login falhas
- Ataques de brute force
- Varreduras de portas (port scanning)
- Análise geográfica de IPs suspeitos
- Exportação de relatórios CSV

Uso:
    python -m log_analyzer --samples --disable-geo
    python -m log_analyzer --firewall logs.csv --auth auth.csv
    analyzer --samples --auto-export

Autor: Security Team
Data: 2024-09-28
Versão: 2.0
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel

from .config import DEFAULT_CONFIG
from .core import LogAnalyzer
from .utils import ensure_directory_exists, validate_file_format

console = Console()


def get_sample_files(format_type="csv"):
    """
    Obtém caminhos para arquivos de exemplo

    Args:
        format_type: 'csv' ou 'json'

    Returns:
        tuple: (firewall_file, auth_file)
    """
    base_dir = Path(__file__).parent.parent.parent
    samples_dir = base_dir / "samples"

    if format_type == "json":
        firewall_file = samples_dir / "firewall_logs.json"
        auth_file = samples_dir / "auth_logs.json"
    else:
        firewall_file = samples_dir / "firewall_logs.csv"
        auth_file = samples_dir / "auth_logs.csv"

    return str(firewall_file), str(auth_file)


def validate_arguments(args):
    """Valida argumentos da linha de comando"""
    if not any([args.firewall, args.auth, args.samples, args.samples_json]):
        console.print(
            "[red]❌ Erro: Especifique arquivos ou use --samples/--samples-json[/red]"
        )
        return False

    if args.firewall and not os.path.exists(args.firewall):
        console.print(
            f"[red]❌ Arquivo de firewall não encontrado: {args.firewall}[/red]"
        )
        return False

    if args.auth and not os.path.exists(args.auth):
        console.print(
            f"[red]❌ Arquivo de autenticação não encontrado: {args.auth}[/red]"
        )
        return False

    return True


def setup_export_directory():
    """Configura diretório de exportação"""
    base_dir = Path(__file__).parent.parent.parent
    exports_dir = base_dir / "exports"
    ensure_directory_exists(exports_dir)
    return exports_dir


def main():
    """Função principal do programa"""
    parser = argparse.ArgumentParser(
        description="Log Analyzer - Ferramenta de Análise de Segurança",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --samples --disable-geo
  %(prog)s --samples-json --auto-export
  %(prog)s --firewall logs.csv --auth auth.csv --export-csv relatorio.csv
  %(prog)s --samples --brute-force-threshold 3 --port-scan-threshold 5
        """,
    )

    # Argumentos de entrada
    input_group = parser.add_argument_group("Arquivos de Entrada")
    input_group.add_argument(
        "--firewall", type=str, help="Arquivo CSV/JSON com logs de firewall"
    )
    input_group.add_argument(
        "--auth", type=str, help="Arquivo CSV/JSON com logs de autenticação"
    )
    input_group.add_argument(
        "--samples", action="store_true", help="Usar arquivos de exemplo (CSV)"
    )
    input_group.add_argument(
        "--samples-json", action="store_true", help="Usar arquivos de exemplo (JSON)"
    )

    # Parâmetros de detecção
    detection_group = parser.add_argument_group("Parâmetros de Detecção")
    detection_group.add_argument(
        "--brute-force-threshold",
        type=int,
        default=5,
        help="Número mínimo de tentativas para detectar brute force (padrão: 5)",
    )
    detection_group.add_argument(
        "--time-window",
        type=int,
        default=1,
        help="Janela de tempo em minutos para detectar brute force (padrão: 1)",
    )
    detection_group.add_argument(
        "--port-scan-threshold",
        type=int,
        default=10,
        help="Número mínimo de portas para detectar port scan (padrão: 10)",
    )
    detection_group.add_argument(
        "--port-scan-window",
        type=int,
        default=1,
        help="Janela de tempo em minutos para detectar port scan (padrão: 1)",
    )

    # Análise geográfica
    geo_group = parser.add_argument_group("Análise Geográfica")
    geo_group.add_argument(
        "--disable-geo",
        action="store_true",
        help="Desabilitar análise geográfica (útil para melhor performance)",
    )
    geo_group.add_argument(
        "--geo-timeout",
        type=int,
        default=5,
        help="Timeout para consultas de geolocalização em segundos (padrão: 5)",
    )

    # Exportação
    export_group = parser.add_argument_group("Exportação de Relatórios")
    export_group.add_argument(
        "--export-csv",
        type=str,
        default=None,
        help="Exportar IPs suspeitos para arquivo CSV (será salvo na pasta exports/)",
    )
    export_group.add_argument(
        "--auto-export",
        action="store_true",
        help="Exportar automaticamente para exports/suspect_ips.csv",
    )

    args = parser.parse_args()

    # Validar argumentos
    if not validate_arguments(args):
        sys.exit(1)

    # Configurar diretório de exportação
    exports_dir = setup_export_directory()

    try:
        # Inicializar analisador com configurações customizadas
        custom_config = DEFAULT_CONFIG.copy()
        custom_config.update(
            {
                "brute_force_threshold": args.brute_force_threshold,
                "time_window_minutes": args.time_window,
                "port_scan_threshold": args.port_scan_threshold,
                "port_scan_window_minutes": args.port_scan_window,
                "geo_timeout": args.geo_timeout,
                "disable_geo": args.disable_geo,
            }
        )

        analyzer = LogAnalyzer(config=custom_config)

        # Exibir cabeçalho
        console.print(
            Panel.fit(
                "[bold blue]🔍 LOG ANALYZER - FERRAMENTA DE ANÁLISE DE SEGURANÇA[/bold blue]\n"
                "[dim]Versão 2.0 - Estrutura Modular[/dim]",
                border_style="blue",
            )
        )
        console.print()

        # Definir arquivos de entrada
        if args.samples:
            firewall_file, auth_file = get_sample_files("csv")
        elif args.samples_json:
            firewall_file, auth_file = get_sample_files("json")
        else:
            firewall_file = args.firewall
            auth_file = args.auth

        # Carregar e analisar logs
        df_firewall = None
        df_auth = None

        if firewall_file:
            console.print("[blue]🔄 Carregando logs de firewall...[/blue]")
            df_firewall = analyzer.load_log_file(firewall_file)

        if auth_file:
            console.print("[blue]🔄 Carregando logs de autenticação...[/blue]")
            df_auth = analyzer.load_log_file(auth_file)

        if df_firewall is None and df_auth is None:
            console.print("[red]❌ Nenhum arquivo válido foi carregado![/red]")
            console.print(
                "[yellow]💡 Verifique os caminhos dos arquivos e tente novamente[/yellow]"
            )
            sys.exit(1)

        console.print()
        console.print("[bold green]🔍 INICIANDO ANÁLISE DE SEGURANÇA...[/bold green]")
        console.print()

        # Executar análises
        if df_firewall is not None:
            console.print("[blue]📊 Analisando logs de firewall...[/blue]")
            analyzer.analyze_firewall_logs(df_firewall)

        if df_auth is not None:
            console.print("[blue]🔐 Analisando tentativas de autenticação...[/blue]")
            analyzer.analyze_auth_logs(df_auth)

        console.print("[blue]🌐 Contando acessos por IP...[/blue]")
        analyzer.count_access_by_ip(df_firewall, df_auth)

        if df_auth is not None:
            console.print(
                f"[blue]⚡ Detectando ataques de brute force ({args.brute_force_threshold}+ tentativas em {args.time_window} min)...[/blue]"
            )
            analyzer.detect_brute_force(
                df_auth, args.time_window, args.brute_force_threshold
            )

        if df_firewall is not None:
            console.print(
                f"[blue]🔍 Detectando varreduras de portas ({args.port_scan_threshold}+ portas em {args.port_scan_window} min)...[/blue]"
            )
            analyzer.detect_port_scanning(
                df_firewall, args.port_scan_window, args.port_scan_threshold
            )

        # Análise geográfica
        if not args.disable_geo and (df_firewall is not None or df_auth is not None):
            console.print(
                "[blue]🌍 Executando análise geográfica dos IPs suspeitos...[/blue]"
            )
            analyzer.analyze_geographic_patterns(
                pd.concat(
                    [df for df in [df_firewall, df_auth] if df is not None],
                    ignore_index=True,
                )
            )
        elif args.disable_geo:
            console.print(
                "[yellow]⏭️  Análise geográfica desabilitada pelo usuário[/yellow]"
            )

        # Gerar resumo final
        console.print("[bold green]📋 GERANDO RESUMO FINAL...[/bold green]")
        console.print()
        analyzer.generate_summary()

        # Exportar resultados se solicitado
        if args.export_csv or args.auto_export:
            console.print()
            console.print("[bold blue]💾 EXPORTANDO RESULTADOS...[/bold blue]")
            console.print()

            if args.export_csv:
                output_file = args.export_csv
            else:
                output_file = "suspect_ips.csv"

            # Se não especificar caminho completo, usar pasta exports
            if not os.path.dirname(output_file):
                output_file = exports_dir / output_file

            analyzer.export_suspect_ips_csv(str(output_file))

        console.print()
        console.print("[bold green]✅ Análise concluída com sucesso![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Análise interrompida pelo usuário[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Erro durante análise: {e}[/red]")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
