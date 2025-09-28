# 🛡️ Log Analyzer - Cybersecurity Tool

[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/henrilopes1/log-analyzer/ci.yml?label=CI%2FCD)](https://github.com/henrilopes1/log-analyzer/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-59%20passing-brightgreen.svg)](https://github.com/henrilopes1/log-analyzer/actions)
[![Coverage](https://img.shields.io/badge/Coverage-35%25-orange.svg)](https://codecov.io/gh/henrilopes1/log-analyzer)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Bandit%20✓-brightgreen.svg)](https://bandit.readthedocs.io/)

Uma ferramenta profissional de análise de logs de segurança desenvolvida em Python, projetada para detectar ameaças cibernéticas, realizar análise geográfica de IPs e gerar relatórios detalhados para profissionais de cybersecurity.er

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Tests](https://img.shields.io/badge/Tests-41%20total-blue.svg)
![Coverage](https://img.shields.io/badge/Coverage-23%25-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Um analisador profissional de logs de segurança desenvolvido em Python com arquitetura modular para detectar ameaças e gerar relatórios detalhados.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/company/log-analyzer)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Uma ferramenta Python avançada para análise de logs de segurança com detecção automática de ameaças, análise geográfica e exportação de relatórios.

## 🎯 Sobre o Projeto

O **Log Analyzer** é uma solução completa para análise de segurança cibernética que processa logs de firewall e autenticação, identificando automaticamente ameaças como ataques de força bruta, varreduras de porta e atividades suspeitas. 

### 🔍 Principais Funcionalidades

- **🚨 Detecção de Ataques**: Identifica brute force, port scanning e tentativas de intrusão
- **🌍 Análise Geográfica**: Rastreamento e localização de IPs maliciosos com API externa
- **📊 Classificação de Riscos**: Sistema inteligente de scoring (Alto/Médio/Baixo risco)
- **� Relatórios Detalhados**: Exportação em CSV e JSON para integração SIEM
- **🎨 Interface Rica**: Visualização colorida e interativa no terminal
- **⚙️ Altamente Configurável**: Parâmetros ajustáveis para diferentes cenários
- **🧪 Testes Abrangentes**: 59 testes automatizados com 35% de cobertura

## � Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/henrilopes1/log-analyzer.git
cd log-analyzer

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar como pacote
pip install -e .
```

## 💡 Como Usar

### Análise com dados de exemplo
```bash
# Análise básica (sem geolocalização)
python -m log_analyzer --samples --disable-geo

# Análise completa com geolocalização
python -m log_analyzer --samples

# Com exportação automática
python -m log_analyzer --samples --auto-export
```

### Análise com arquivos personalizados
```bash
# Arquivos específicos
python -m log_analyzer --firewall firewall.csv --auth auth.csv

# Com parâmetros customizados
python -m log_analyzer --firewall logs.csv --brute-force-threshold 3
```

## 📊 Exemplo de Saída

```
🛡️ TENTATIVAS BLOQUEADAS PELO FIREWALL
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ IP de Origem  ┃ Tentativas      ┃ Portas Alvo     ┃ Protocolos      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 94.102.49.123 │       15        │ 22, 80, 443     │ TCP, UDP        │
│ 203.0.113.15  │        8        │ 22, 3389        │ TCP             │
└───────────────┴──────────────────┴──────────────────┴──────────────────┘

🚨 ATAQUES DE BRUTE FORCE DETECTADOS!
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ IP Atacante   ┃ Tentativas      ┃ Usuários Alvo   ┃ Serviços        ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 192.168.1.100 │       12        │ admin, root     │ ssh, ftp        │
└───────────────┴──────────────────┴──────────────────┴──────────────────┘
```

## 🏗️ Arquitetura do Projeto

```
log-analyzer/
├── 📁 src/log_analyzer/           # Código principal
│   ├── core.py                   # Motor de análise
│   ├── geographic.py             # Análise geográfica
│   ├── utils.py                  # Funções utilitárias
│   └── config.py                 # Configurações
├── 📁 tests/                     # Testes automatizados (59 testes)
├── 📁 samples/                   # Logs de exemplo
├── 📁 exports/                   # Relatórios gerados
├── 📁 .github/workflows/         # CI/CD com GitHub Actions
├── 📁 scripts/                   # Scripts de automação
└── requirements.txt              # Dependências
```

## � Tecnologias Utilizadas

- **Python 3.9+**: Linguagem principal
- **Pandas**: Processamento de dados
- **Rich**: Interface visual no terminal  
- **Requests**: Consultas de geolocalização
- **Pytest**: Framework de testes
- **GitHub Actions**: CI/CD automatizado
- **Docker**: Containerização

## 🧪 Qualidade e Testes

O projeto possui uma robusta suite de testes e pipeline de CI/CD:

- ✅ **59 testes automatizados** (100% de aprovação)
- 📊 **35% de cobertura de código** (em expansão)
- 🔒 **0 vulnerabilidades** de segurança (Bandit)
- 🤖 **CI/CD automatizado** com GitHub Actions
- 📦 **Build e deploy** automatizados
- 🐳 **Containerização** com Docker

```bash
# Executar testes localmente
pytest tests/ -v

# Com relatório de cobertura
pytest --cov=src --cov-report=html

# Pipeline completo local
python scripts/ci_cd_local.py
```

## 🛠️ Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Formatação automática
make format

# Verificação de qualidade
make lint

# Executar todos os checks
make ci
```

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Desenvolvedor

**Henri Lopes**
- 🐙 GitHub: [@henrilopes1](https://github.com/henrilopes1)
- � Contato: [henri@example.com]

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!**