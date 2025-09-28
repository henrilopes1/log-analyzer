# Documentação do Log Analyzer

Esta pasta contém a documentação técnica detalhada do Log Analyzer.

## Arquivos de Documentação

### `API.md`
Documentação da API interna das classes e métodos.

### `ARCHITECTURE.md`
Descrição da arquitetura do sistema e decisões de design.

### `CHANGELOG.md`
Histórico de mudanças e versões.

### `CONTRIBUTING.md`
Guia para contribuições ao projeto.

### `DEPLOYMENT.md`
Instruções de implantação em diferentes ambientes.

### `EXAMPLES.md`
Exemplos práticos de uso da ferramenta.

### `FAQ.md`
Perguntas frequentes e soluções de problemas.

## Estrutura do Projeto

```
log-analyzer/
├── src/
│   └── log_analyzer/           # Pacote principal
│       ├── __init__.py         # Inicialização do pacote
│       ├── core.py            # Classe principal LogAnalyzer
│       ├── geographic.py      # Análise geográfica
│       ├── config.py          # Configurações
│       └── utils.py           # Utilitários
├── tests/                     # Testes automatizados
├── docs/                      # Documentação
├── config/                    # Arquivos de configuração
├── samples/                   # Dados de exemplo
├── exports/                   # Relatórios exportados
├── main.py                    # Script original (compatibilidade)
├── run_analyzer.py            # Script refatorado
├── requirements.txt           # Dependências
└── README.md                  # Documentação principal
```

## Começando

1. **Instalação básica**: Veja o README.md principal
2. **Exemplos de uso**: Consulte EXAMPLES.md
3. **API técnica**: Consulte API.md
4. **Contribuições**: Veja CONTRIBUTING.md

Para mais informações, consulte os arquivos específicos nesta pasta.