# 🛡️ Log Analyzer - Cybersecurity Tool

Uma ferramenta profissional de análise de logs de segurança desenvolvida em Python, contendo um **Core Analítico**, uma **API REST FastAPI** e um **Dashboard Web interativo (Streamlit)** para facilitar a leitura. O projeto é focado em detectar ameaças cibernéticas locais, realizar curadoria geográfica de IPs e gerar insights visuais em painéis de análise rápida.

## 🎯 Sobre o Projeto

O **Log Analyzer** é uma solução para análise de segurança cibernética que processa logs de firewall e autenticação em busca de comportamentos suspeitos, exibindo os resultados tanto para sistemas automatizados (via API) quanto para humanos (através de uma bela interface gráfica).

### 🔍 Principais Funcionalidades

- **🚨 Detecção de Ameaças**: Identifica acessos de força bruta e comportamentos de ataque.
- **🌍 Mapeamento Geográfico**: Integração de chaves visuais com mapa-múndi e geolocalização dos IPs invasores.
- **📊 Inteligência de Risco**: Sistema de classificação baseada no histórico de atividade local (Alto/Médio/Baixo).
- **🌐 Pipeline REST**: Um backend em FastAPI pronto para receber cargas em formatos `.json` ou `.csv`.
- **💻 App Web (Frontend)**: Interface limpa rodando sobre o *Streamlit* para upload simultâneo e construção em tempo real dos dashboards.
- **⚙️ Limpo e Desacoplado**: Repositório focado com arquivos independentes e código desacoplado.

---

## ⚡ Instalação Rápida

Recomenda-se utilizar um ambiente virtual (`.venv`) para rodar e testar esta ferramenta na sua máquina local:

```bash
# 1. Clonar o repositório
git clone https://github.com/henrilopes1/log-analyzer.git
cd log-analyzer

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar o ambiente
source .venv/Scripts/activate  # Linux/Git Bash/Mac
.venv\Scripts\activate         # Windows (CMD)

# 4. Instalar as dependências do Back e Front
pip install -r requirements.txt
pip install streamlit requests pandas
```

---

## 💡 Como Usar o Projeto

Para visualizar a ferramenta em seu potencial completo, você deve ligar o Backend e, em seguida, o Frontend.

### 1️⃣ Iniciando a API (Backend)
No seu terminal (com o ambiente `venv` ativo):
```bash
python run_api.py
```
A API ficará ativa em `http://127.0.0.1:8000`. Ela é quem realiza a leitura pesada dos dados CSV.

### 2️⃣ Iniciando o Dashboard Web (Frontend)
Abra um segundo terminal integrado, ative novamente o seu virtual environment (`.venv`) e rode o Streamlit:
```bash
python -m streamlit run frontend/web_app.py
```
O framework abrirá uma nova guia no seu navegador em `http://localhost:8501`. 

### 3️⃣ Testando
1. No menu lateral da página, arraste os arquivos de exemplo contidos na pasta `./data/` do projeto (`sample_firewall.csv` e `sample_auth.csv`).
2. Clique no botão de enviar.
3. Observe os contadores de ameaças, a Tabela de Alertas de Nível Alto e a Localização dos Ofensores sendo exibidos em tempo real.

---

## 🔧 Arquitetura do Projeto

A estrutura do diretório foi limpa para priorizar o foco na regra de negócios:

```text
log-analyzer/
├── data/                # Bases de dados simuladas para poder fazer os testes
├── docs/                # Arquivos complementares de documentação
├── examples/            # Exemplos de uso limpo (ex: test_geographic.py)
├── frontend/            # A interface Web do dashboard (web_app.py)
├── src/                 # Lógica de Backend (A regra de negócios do app LogAnalyzer e a API)
├── tests/               # Testes de unidade e qualidade (via Pytest)
│
├── CHANGELOG.md         # Histórico de alterações e features do sistema
├── COMO_EXECUTAR.md     # Instruções em detalhes
├── run_api.py           # O "botão de ligar" do seu Servidor FastAPI
└── README.md            # Este arquivo principal
```

---

## 📊 Endpoints Diretos da API

Se você preferir consumir o serviço via outro app em vez do Streamlit, basta bater nestes caminhos (com a aplicação `run_api.py` ativa): 

- **GET `/`** - Status da API
- **GET `/health`** - Health check
- **POST `/analyze/`** - Análise de logs (envio via body multipart)
- **GET `/docs`** - Documentação interativa (Swagger UI nativo)

---

## 👨‍💻 Autor

**Henri Lopes**
- GitHub: [@henrilopes1](https://github.com/henrilopes1)
- LinkedIn: [Henri Lopes](https://www.linkedin.com/in/henri-de-oliveira-lopes)

<div align="center">
  <strong>🛡️ Mantenha seus logs seguros com o Log Analyzer Cyber! 🛡️</strong>
</div>
