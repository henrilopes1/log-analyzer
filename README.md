# 🛡️ Log Analyzer - Cybersecurity Tool

[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/henrilopes1/log-analyzer/ci.yml?label=CI%2FCD)](https://github.com/henrilopes1/log-analyzer/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-59%20passing-brightgreen.svg)](https://github.com/henrilopes1/log-analyzer/actions)
[![Coverage](https://img.shields.io/badge/Coverage-35%25-orange.svg)](https://codecov.io/gh/henrilopes1/log-analyzer)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Bandit%20✓-brightgreen.svg)](https://bandit.readthedocs.io/)
[![API](https://img.shields.io/badge/API-REST%20FastAPI-green.svg)](http://127.0.0.1:8000/docs)

Uma ferramenta profissional de análise de logs de segurança desenvolvida em Python, com **API REST FastAPI integrada**, projetada para detectar ameaças cibernéticas, realizar análise geográfica de IPs e gerar relatórios detalhados para profissionais de cybersecurity.

## 🎯 Sobre o Projeto

O **Log Analyzer** é uma solução completa para análise de segurança cibernética que processa logs de firewall e autenticação, identificando automaticamente ameaças como ataques de força bruta, varreduras de porta e atividades suspeitas. 

### 🔍 Principais Funcionalidades

- **🚨 Detecção de Ataques**: Identifica brute force, port scanning e tentativas de intrusão
- **🌍 Análise Geográfica**: Rastreamento e localização de IPs maliciosos com API externa
- **📊 Classificação de Riscos**: Sistema inteligente de scoring (Alto/Médio/Baixo risco)
- **📋 Relatórios Detalhados**: Exportação em CSV e JSON para integração SIEM
- **🎨 Interface Rica**: Visualização colorida e interativa no terminal
- **🌐 API REST**: Interface FastAPI para integração com outras aplicações
- **⚙️ Altamente Configurável**: Parâmetros ajustáveis para diferentes cenários
- **🧪 Testes Abrangentes**: 59+ testes automatizados com 35% de cobertura
- **🐳 Containerização**: Suporte completo Docker e Docker Compose

## ⚡ Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/henrilopes1/log-analyzer.git
cd log-analyzer

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências (incluindo API)
make api-install
# ou manualmente:
pip install -r requirements.txt

# Instalar como pacote
pip install -e .
```

## 💡 Como Usar

### 🖥️ Linha de Comando

#### Análise com dados de exemplo
```bash
# Análise básica (sem geolocalização)
python -m log_analyzer --samples --disable-geo

# Análise completa com geolocalização
python -m log_analyzer --samples

# Com exportação automática
python -m log_analyzer --samples --auto-export
```

#### Análise com arquivos personalizados
```bash
# Arquivos específicos
python -m log_analyzer --firewall firewall.csv --auth auth.csv

# Com parâmetros customizados
python -m log_analyzer --firewall logs.csv --brute-force-threshold 3
```

### 🌐 API REST

#### Iniciar o servidor da API
```bash
# Desenvolvimento com reload automático
make api-dev
# ou
python run_api.py --reload --debug

# Produção
make api-prod
# ou
python run_api.py --prod --host 0.0.0.0
```

#### Endpoints disponíveis
- **GET /** - Status da API
- **GET /health** - Health check
- **POST /analyze/** - Análise de logs com upload de arquivos
- **GET /api-info** - Informações da API
- **GET /docs** - Documentação interativa (Swagger UI)
- **GET /redoc** - Documentação ReDoc

#### Exemplo de uso da API
```bash
# Testar status
curl http://127.0.0.1:8000/

# Analisar logs
curl -X POST "http://127.0.0.1:8000/analyze/" \
  -F "firewall_log=@firewall.csv" \
  -F "auth_log=@auth.csv"

# Ou usar o cliente de exemplo
python examples/api_client_example.py --analyze data/sample_firewall.csv
```

### 🐳 Docker

#### Executar com Docker Compose
```bash
# Iniciar serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

#### Construir imagem personalizada
```bash
# Construir imagem da API
docker build -f Dockerfile.api -t log-analyzer-api .

# Executar container
docker run -p 8000:8000 log-analyzer-api
```

## 🛠️ Desenvolvimento

### Comandos Make úteis
```bash
# Instalar dependências de desenvolvimento
make install-dev

# Executar todos os testes
make test

# Testes com cobertura
make test-cov

# Verificação de qualidade de código
make lint
make format
make security

# API - comandos específicos
make api-dev          # Servidor de desenvolvimento
make api-test         # Testes da API
make api-demo         # Demo completa
make api-docs         # Informações sobre documentação
```

### CI/CD Pipeline

O projeto inclui pipeline completo de CI/CD com:
- **Testes automatizados** em múltiplas versões Python
- **Análise de qualidade** (Black, isort, flake8, mypy)
- **Verificação de segurança** (Bandit, Safety)
- **Build Docker** automatizado
- **Verificação de dependências**
- **Deploy automático** com tags

## 🔧 Arquitetura

```
log-analyzer/
├── src/log_analyzer/        # Código principal
│   ├── core.py             # Analisador principal
│   ├── geographic.py       # Análise geográfica
│   ├── api.py              # API REST FastAPI
│   └── utils.py            # Utilitários
├── tests/                  # Testes
│   ├── test_api.py         # Testes da API
│   └── test_*.py          # Demais testes
├── examples/               # Exemplos de uso
│   └── api_client_example.py
├── docker-compose.yml      # Orquestração
├── Dockerfile.api         # Container da API
├── run_api.py            # Script para executar API
└── Makefile              # Comandos automatizados
```

## 📊 Recursos da API

### Upload de Arquivos
- **Formatos suportados**: CSV, JSON
- **Tipos de logs**: Firewall, Autenticação
- **Tamanho máximo**: 100MB por arquivo
- **Processamento**: Análise em tempo real

### Análises Disponíveis
- **Detecção de força bruta**: Tentativas repetidas de login
- **Varredura de porta**: Identificação de port scanning
- **Análise geográfica**: Localização de IPs suspeitos
- **Classificação de risco**: Alto, médio e baixo risco
- **Estatísticas detalhadas**: Resumos quantitativos

### Respostas JSON
```json
{
  "summary": {
    "files_processed": 2,
    "total_events": 1000,
    "analysis_completed": true
  },
  "brute_force_attacks": [...],
  "geographic_analysis": [...],
  "top_suspicious_ips": [...],
  "alerts": {
    "high_risk": [...],
    "medium_risk": [...],
    "low_risk": [...]
  }
}
```

## 📚 Documentação

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **Exemplos de uso**: Diretório `examples/`
- **Testes**: `python tests/test_api.py --url http://127.0.0.1:8000`

## 🧪 Testes

```bash
# Testes da aplicação
make test

# Testes específicos da API
python tests/test_api.py

# Demo completa
make api-demo
```

## 🤝 Contribuições

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Henri Lopes**
- GitHub: [@henrilopes1](https://github.com/henrilopes1)
- LinkedIn: [Henri Lopes](https://www.linkedin.com/in/henri-de-oliveira-lopes)

---

<div align="center">
  <strong>🛡️ Mantenha seus logs seguros com Log Analyzer! 🛡️</strong>
</div>
