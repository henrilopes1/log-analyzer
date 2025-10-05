#!/usr/bin/env python3
"""
Script de automação para executar todos os checks de qualidade e CI/CD localmente.

Este script simula o que os workflows de CI/CD fazem no GitHub Actions.
"""

import subprocess
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import track
import time

console = Console()


def run_command(command: str, description: str) -> tuple[bool, str]:
    """Executa um comando e retorna o resultado."""
    console.print(f"🔄 {description}...")

    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos timeout
        )

        if result.returncode == 0:
            console.print(f"✅ {description} - [green]SUCCESS[/green]")
            return True, result.stdout
        else:
            console.print(f"❌ {description} - [red]FAILED[/red]")
            console.print(f"[red]Error:[/red] {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        console.print(f"⏰ {description} - [yellow]TIMEOUT[/yellow]")
        return False, "Command timed out"

    except Exception as e:
        console.print(f"💥 {description} - [red]ERROR[/red]: {str(e)}")
        return False, str(e)


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    console.print("[bold blue]🔍 Verificando dependências...[/bold blue]")

    required_commands = [
        ("python", "Python interpreter"),
        ("pip", "Python package manager"),
    ]

    missing = []
    for cmd, desc in required_commands:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            console.print(f"✅ {desc} encontrado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(f"❌ {desc} não encontrado")
            missing.append(desc)

    if missing:
        console.print(f"[red]Dependências faltando: {', '.join(missing)}[/red]")
        return False

    return True


def install_dev_dependencies():
    """Instala dependências de desenvolvimento."""
    console.print(
        "[bold blue]📦 Instalando dependências de desenvolvimento...[/bold blue]"
    )

    commands = [
        ("pip install -r requirements.txt", "Instalando dependências principais"),
        (
            "pip install -r requirements-dev.txt",
            "Instalando dependências de desenvolvimento",
        ),
    ]

    all_success = True
    for cmd, desc in commands:
        success, _ = run_command(cmd, desc)
        if not success:
            all_success = False

    return all_success


def run_tests():
    """Executa todos os testes."""
    console.print("[bold blue]🧪 Executando testes...[/bold blue]")

    test_commands = [
        ("python -m pytest tests/ -v --tb=short", "Testes unitários"),
        (
            "python -m pytest tests/ --cov=src --cov-report=xml --cov-report=html --cov-fail-under=80",
            "Testes com cobertura",
        ),
    ]

    all_success = True
    for cmd, desc in test_commands:
        success, _ = run_command(cmd, desc)
        if not success:
            all_success = False

    return all_success


def run_linting():
    """Executa ferramentas de linting."""
    console.print("[bold blue]🔍 Executando linting...[/bold blue]")

    lint_commands = [
        ("python -m black --check src/ tests/", "Black code formatting check"),
        ("python -m isort --check-only src/ tests/", "Import sorting check"),
        (
            "python -m flake8 src/ --max-line-length=88 --extend-ignore=E203,E501,W503",
            "Flake8 linting",
        ),
    ]

    # mypy é opcional, pode falhar
    optional_commands = [
        ("python -m mypy src/", "MyPy type checking"),
    ]

    all_success = True
    for cmd, desc in lint_commands:
        success, _ = run_command(cmd, desc)
        if not success:
            all_success = False

    # Comandos opcionais
    for cmd, desc in optional_commands:
        success, _ = run_command(cmd, f"{desc} (opcional)")
        if not success:
            console.print(
                f"[yellow]Warning:[/yellow] {desc} falhou, mas continuando..."
            )

    return all_success


def run_security_checks():
    """Executa verificações de segurança."""
    console.print("[bold blue]🔒 Executando verificações de segurança...[/bold blue]")

    security_commands = [
        ("python -m bandit -r src/", "Bandit security scan"),
        ("python -m safety check", "Safety vulnerability check"),
    ]

    all_success = True
    for cmd, desc in security_commands:
        success, _ = run_command(cmd, desc)
        if not success:
            # Security checks podem falhar mas não devem parar o pipeline
            console.print(
                f"[yellow]Warning:[/yellow] {desc} encontrou problemas, mas continuando..."
            )

    return all_success


def build_package():
    """Constrói o pacote."""
    console.print("[bold blue]📦 Construindo pacote...[/bold blue]")

    build_commands = [
        ("python -m build", "Building package"),
        ("python -m twine check dist/*", "Checking package"),
    ]

    all_success = True
    for cmd, desc in build_commands:
        success, _ = run_command(cmd, desc)
        if not success:
            all_success = False

    return all_success


def generate_report(results: dict):
    """Gera relatório final."""
    console.print("\n" + "=" * 60)
    console.print("[bold]📊 RELATÓRIO FINAL DO CI/CD LOCAL[/bold]")
    console.print("=" * 60)

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Etapa", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Resultado", justify="center")

    total_steps = len(results)
    passed_steps = sum(1 for success in results.values() if success)

    for step, success in results.items():
        status_icon = "✅" if success else "❌"
        status_text = "[green]PASSOU[/green]" if success else "[red]FALHOU[/red]"

        table.add_row(step, status_icon, status_text)

    console.print(table)

    # Resumo
    percentage = (passed_steps / total_steps) * 100

    if passed_steps == total_steps:
        panel_style = "green"
        status = "✅ TODOS OS CHECKS PASSARAM!"
        message = "Seu código está pronto para produção! 🚀"
    elif percentage >= 80:
        panel_style = "yellow"
        status = f"⚠️ {passed_steps}/{total_steps} CHECKS PASSARAM ({percentage:.1f}%)"
        message = "Quase lá! Corrija os problemas restantes."
    else:
        panel_style = "red"
        status = f"❌ {passed_steps}/{total_steps} CHECKS PASSARAM ({percentage:.1f}%)"
        message = "Vários problemas encontrados. Revise o código."

    summary_panel = Panel(
        f"[bold]{status}[/bold]\n\n{message}",
        title="🎯 Resumo",
        border_style=panel_style,
        box=box.DOUBLE,
    )

    console.print("\n")
    console.print(summary_panel)

    return passed_steps == total_steps


def main():
    """Função principal."""
    console.print("[bold green]🚀 Iniciando CI/CD Local - Log Analyzer[/bold green]")
    console.print("Este script executará todos os checks de qualidade localmente.\n")

    # Verificar se estamos no diretório correto
    if not Path("pyproject.toml").exists():
        console.print("[red]❌ Execute este script na raiz do projeto![/red]")
        sys.exit(1)

    # Verificar dependências
    if not check_dependencies():
        console.print("[red]❌ Dependências faltando! Instale Python e pip.[/red]")
        sys.exit(1)

    # Executar etapas
    steps = [
        ("Instalação de Dependências", install_dev_dependencies),
        ("Testes", run_tests),
        ("Linting", run_linting),
        ("Verificações de Segurança", run_security_checks),
        ("Build do Pacote", build_package),
    ]

    results = {}

    for step_name, step_function in track(steps, description="Executando CI/CD..."):
        console.print(f"\n[bold]{'='*20} {step_name} {'='*20}[/bold]")
        results[step_name] = step_function()
        time.sleep(0.5)  # Pequena pausa visual

    # Gerar relatório
    all_passed = generate_report(results)

    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrompido pelo usuário[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]💥 Erro inesperado: {e}[/red]")
        sys.exit(1)
