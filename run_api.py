#!/usr/bin/env python
"""
Script para iniciar o servidor da API Log Analyzer

Este script fornece uma maneira fácil de iniciar o servidor FastAPI
com configurações apropriadas para desenvolvimento e produção.

Uso:
    python run_api.py [--host HOST] [--port PORT] [--reload] [--prod]

Exemplos:
    python run_api.py                    # Desenvolvimento padrão (localhost:8000)
    python run_api.py --reload           # Com reload automático
    python run_api.py --host 0.0.0.0     # Acesso externo
    python run_api.py --port 8080        # Porta personalizada
    python run_api.py --prod             # Modo produção
"""

import argparse
import sys
import logging
from pathlib import Path

try:
    import uvicorn
except ImportError:
    print("❌ Uvicorn não está instalado. Execute: pip install uvicorn[standard]")
    sys.exit(1)


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the API server."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main function to start the API server."""
    parser = argparse.ArgumentParser(
        description="Iniciar servidor da API Log Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host para bind do servidor (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta para o servidor (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Ativar reload automático durante desenvolvimento"
    )
    
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Modo produção (desativa reload e debug)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Número de workers (modo produção, default: 1)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativar logs de debug"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Verificar se o módulo da API existe
    api_module = Path(__file__).parent / "src" / "log_analyzer" / "api.py"
    if not api_module.exists():
        print("❌ Módulo da API não encontrado. Verifique se o arquivo api.py existe.")
        sys.exit(1)
    
    # Configurações do servidor
    config = {
        "app": "src.log_analyzer.api:app",
        "host": args.host,
        "port": args.port,
        "log_level": "debug" if args.debug else "info",
    }
    
    if args.prod:
        # Configurações de produção
        config.update({
            "workers": args.workers,
            "reload": False,
            "access_log": True,
        })
        print(f"🚀 Iniciando servidor em modo PRODUÇÃO:")
        print(f"   📍 URL: http://{args.host}:{args.port}")
        print(f"   👥 Workers: {args.workers}")
        print(f"   📚 Docs: http://{args.host}:{args.port}/docs")
    else:
        # Configurações de desenvolvimento
        config.update({
            "reload": args.reload,
            "reload_dirs": ["src"],
        })
        print(f"🔧 Iniciando servidor em modo DESENVOLVIMENTO:")
        print(f"   📍 URL: http://{args.host}:{args.port}")
        print(f"   🔄 Reload: {'Ativado' if args.reload else 'Desativado'}")
        print(f"   📚 Docs: http://{args.host}:{args.port}/docs")
        print(f"   📖 ReDoc: http://{args.host}:{args.port}/redoc")
    
    print(f"\n✨ Endpoints disponíveis:")
    print(f"   GET  /           - Status da API")
    print(f"   GET  /health     - Health check")
    print(f"   POST /analyze/   - Análise de logs")
    print(f"   GET  /api-info   - Informações da API")
    
    print(f"\n📝 Para testar a API:")
    print(f"   curl http://{args.host}:{args.port}/")
    print(f"\n⏹️  Para parar: Ctrl+C")
    print(f"{'='*60}")
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()