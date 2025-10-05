#!/usr/bin/env python
"""
Script otimizado para iniciar o servidor da API Log Analyzer

Aplicando boas práticas de programação com:
- Tratamento de erros robusto
- Configuração centralizada
- Logging adequado
- Validação de dependências
"""

import argparse
import logging
import sys
from pathlib import Path

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constantes
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_WORKERS = 1


def check_dependencies() -> bool:
    """Verifica se as dependências necessárias estão disponíveis."""
    try:
        import uvicorn

        logger.info("✅ Uvicorn disponível")
        return True
    except ImportError:
        logger.error(
            "❌ Uvicorn não encontrado. Execute: pip install uvicorn[standard]"
        )
        return False


def validate_project_structure() -> bool:
    """Valida se a estrutura do projeto está correta."""
    api_module = Path(__file__).parent / "src" / "log_analyzer" / "api.py"
    if not api_module.exists():
        logger.error(f"❌ Módulo API não encontrado: {api_module}")
        return False

    logger.info("✅ Estrutura do projeto validada")
    return True


def get_server_config(args) -> dict:
    """Prepara configuração do servidor."""
    config = {
        "app": "src.log_analyzer.api:app",
        "host": args.host,
        "port": args.port,
        "log_level": "debug" if args.debug else "info",
    }

    if args.prod:
        config.update(
            {
                "workers": args.workers,
                "reload": False,
                "access_log": True,
            }
        )
    else:
        config.update(
            {
                "reload": args.reload,
                "reload_dirs": ["src"] if args.reload else None,
            }
        )

    return config


def print_startup_info(args) -> None:
    """Imprime informações de inicialização."""
    mode = "PRODUÇÃO" if args.prod else "DESENVOLVIMENTO"

    logger.info(f"🚀 Iniciando servidor em modo {mode}")
    logger.info(f"📍 URL: http://{args.host}:{args.port}")

    if args.prod:
        logger.info(f"👥 Workers: {args.workers}")
    else:
        logger.info(f"🔄 Reload: {'Ativado' if args.reload else 'Desativado'}")

    logger.info(f"📚 Documentação: http://{args.host}:{args.port}/docs")

    # Endpoints
    endpoints = [
        "GET  /           - Status da API",
        "GET  /health     - Health check",
        "POST /analyze/   - Análise de logs",
        "GET  /api-info   - Informações da API",
    ]

    logger.info("✨ Endpoints disponíveis:")
    for endpoint in endpoints:
        logger.info(f"   {endpoint}")

    logger.info(f"📝 Teste: curl http://{args.host}:{args.port}/")
    logger.info("⏹️  Para parar: Ctrl+C")


def create_parser() -> argparse.ArgumentParser:
    """Cria parser de argumentos."""
    parser = argparse.ArgumentParser(
        description="Iniciar servidor da API Log Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host para bind do servidor (default: {DEFAULT_HOST})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Porta para o servidor (default: {DEFAULT_PORT})",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Ativar reload automático (desenvolvimento)",
    )

    parser.add_argument(
        "--prod", action="store_true", help="Modo produção (desativa reload e debug)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Número de workers (produção, default: {DEFAULT_WORKERS})",
    )

    parser.add_argument("--debug", action="store_true", help="Ativar logs de debug")

    return parser


def main() -> None:
    """Função principal."""
    parser = create_parser()
    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🐛 Modo debug ativado")

    # Validações
    if not check_dependencies():
        sys.exit(1)

    if not validate_project_structure():
        sys.exit(1)

    # Configurar servidor
    config = get_server_config(args)

    # Imprimir informações
    print_startup_info(args)
    print("=" * 60)

    # Iniciar servidor
    try:
        import uvicorn

        uvicorn.run(**config)

    except KeyboardInterrupt:
        logger.info("👋 Servidor parado pelo usuário")

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
