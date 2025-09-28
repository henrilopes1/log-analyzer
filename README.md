# � Log Analyzer

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Tests](https://img.shields.io/badge/Tests-41%20total-blue.svg)
![Coverage](https://img.shields.io/badge/Coverage-23%25-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Um analisador profissional de logs de segurança desenvolvido em Python com arquitetura modular para detectar ameaças e gerar relatórios detalhados.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/company/log-analyzer)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Uma ferramenta Python avançada para análise de logs de segurança com detecção automática de ameaças, análise geográfica e exportação de relatórios.

## ✨ Características

- 🔍 **Detecção Automática**: Identifica brute force, port scanning e tentativas de login falhadas
- 🌍 **Análise Geográfica**: Localização de IPs suspeitos com detecção de anomalias
- 📊 **Classificação de Riscos**: Sistema inteligente de scoring (Alto/Médio/Baixo)
- 💾 **Exportação CSV**: Relatórios estruturados para integração SIEM
- 🎨 **Interface Visual**: Tabelas e painéis coloridos com Rich
- ⚙️ **Configurável**: Parâmetros ajustáveis para detecção
- 📦 **Estrutura Modular**: Código organizado seguindo boas práticas Python

## 🚀 Formas de Uso

### **Opção 1: Comando Instalado (Recomendado)**
```bash
# Instalar como pacote
pip install -e .

# Usar comando global
analyzer --samples --disable-geo
analyzer --samples-json --auto-export
```

### **Opção 2: Módulo Python**
```bash
# Executar como módulo
python -m src.log_analyzer --samples
python -m log_analyzer --samples --auto-export
```

### **Opção 3: Wrapper de Compatibilidade**
```bash
# Usar wrapper (deprecated)
python main.py --samples --disable-geo
```

## 📥 Instalação

```bash
# Clonar o repositório
git clone https://github.com/company/log-analyzer.git
cd log-analyzer

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar como pacote (recomendado)
pip install -e .
```

## 🎯 Exemplos de Uso

### **Análise Rápida com Dados de Exemplo**
```bash
# Análise básica
analyzer --samples --disable-geo

# Com exportação automática
analyzer --samples --auto-export

# Formato JSON
analyzer --samples-json --disable-geo
```

### **Análise com Arquivos Personalizados**
```bash
# Arquivos específicos
analyzer --firewall firewall.csv --auth auth.csv

# Com parâmetros customizados
analyzer --firewall logs.csv --brute-force-threshold 3 --port-scan-threshold 5

# Com análise geográfica
analyzer --auth auth.csv --geo-timeout 10
```

### **Exportação de Relatórios**
```bash
# Exportação automática
analyzer --samples --auto-export

# Arquivo personalizado
analyzer --samples --export-csv "relatorio_$(date +%Y%m%d).csv"
```

## 🔧 Parâmetros de Configuração

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--brute-force-threshold` | 5 | Tentativas mínimas para detectar brute force |
| `--time-window` | 1 | Janela de tempo em minutos |
| `--port-scan-threshold` | 10 | Portas mínimas para detectar port scan |
| `--port-scan-window` | 1 | Janela de tempo para port scan |
| `--geo-timeout` | 5 | Timeout para consultas geográficas |
| `--disable-geo` | - | Desabilitar análise geográfica |

## 📊 Formatos de Entrada

### **CSV de Firewall**
```csv
timestamp,source_ip,dest_ip,dest_port,protocol,action
2024-09-28 11:00:10,94.102.49.123,10.0.0.50,22,TCP,BLOCK
```

### **CSV de Autenticação**
```csv
timestamp,username,source_ip,action,service,user_agent
2024-09-28 09:30:45,admin,203.0.113.15,FAILED,SSH,OpenSSH_7.4
```

### **JSON (Alternativo)**
```json
[
  {
    "timestamp": "2024-09-28 11:00:10",
    "source_ip": "94.102.49.123",
    "dest_ip": "10.0.0.50",
    "dest_port": 22,
    "protocol": "TCP",
    "action": "BLOCK"
  }
]
```

## 📁 Estrutura do Projeto

```
log-analyzer/
├── 📁 src/log_analyzer/           # Código modular principal
│   ├── __init__.py               # Configuração do pacote
│   ├── __main__.py               # Ponto de entrada do módulo
│   ├── main.py                   # Função principal
│   ├── core.py                   # LogAnalyzer (classe principal)
│   ├── geographic.py             # Análise geográfica
│   ├── utils.py                  # Funções utilitárias
│   └── config.py                 # Configurações
├── 📁 samples/                   # Logs de exemplo
├── 📁 exports/                   # Relatórios gerados
├── 📁 config/                    # Configurações externas
├── 📁 legacy/                    # Código original (compatibilidade)
├── 📁 tests/                     # Testes unitários
├── 📁 docs/                      # Documentação
├── main.py                       # Wrapper de compatibilidade
├── setup.py                      # Configuração de instalação
└── requirements.txt              # Dependências
```

## 🛠️ Desenvolvimento

### **Executar Testes**
```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src/log_analyzer --cov-report=html
```

### **Formatação de Código**
```bash
# Black (formatação)
black src/

# Flake8 (linting)
flake8 src/

# MyPy (type checking)
mypy src/
```

### **Instalar para Desenvolvimento**
```bash
pip install -e ".[dev]"
```

## 🔍 Funcionalidades Detectadas

### **🚨 Ataques de Brute Force**
- Múltiplas tentativas de login falhadas
- Janela de tempo configurável
- Detecção por IP, usuário e serviço

### **🔍 Port Scanning**
- Varredura de múltiplas portas
- Análise de taxa de tentativas
- Detecção de reconnaissance

### **🌍 Análise Geográfica**
- Localização de IPs suspeitos
- Detecção de concentrações anômalas
- Informações de ISP e região

### **📊 Classificação de Riscos**
- 🔴 **Alto Risco**: >10 acessos ou ataques confirmados
- 🟡 **Médio Risco**: 5-10 acessos
- 🟢 **Baixo Risco**: <5 acessos

## 📈 Saídas e Relatórios

### **Console (Rich Interface)**
- Tabelas coloridas e formatadas
- Painéis informativos
- Barras de progresso em tempo real

### **Arquivo CSV (exports/)**
```csv
ip,tipo_de_alerta,quantidade_de_ocorrencias
203.0.113.15,BRUTE_FORCE,6
94.102.49.123,PORT_SCAN,13
```

## 🔄 Migração da Versão 1.x

A versão 2.0 mantém **compatibilidade completa** com scripts antigos:

```bash
# ❌ Versão antiga (ainda funciona)
python main.py --samples

# ✅ Versão nova (recomendada)
analyzer --samples
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Security Team**
- 📧 Email: security@company.com
- 🐙 GitHub: [@security-team](https://github.com/security-team)

## 🆘 Suporte

- 📚 [Documentação](https://log-analyzer.readthedocs.io/)
- 🐛 [Issues](https://github.com/company/log-analyzer/issues)
- 💬 [Discussions](https://github.com/company/log-analyzer/discussions)

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**