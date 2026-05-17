# 🛡️ Log Analyzer - Cybersecurity Tool

Uma ferramenta profissional de análise de logs de segurança desenvolvida em Python, contendo um **Core Analítico**, uma **API REST FastAPI protegida com JWT** e um **Dashboard Web interativo (Streamlit)** moderno e seguro para facilitar a leitura e análise de ameaças. O projeto é focado em detectar ataques cibernéticos locais, realizar curadoria geográfica de IPs e gerar insights visuais rápidos em um painel restrito.

## 🎯 Sobre o Projeto

O **Log Analyzer** é uma solução para análise de segurança cibernética que processa logs de firewall e autenticação em busca de comportamentos suspeitos. Agora conta com um **fluxo de login restrito via JWT**, garantindo que apenas usuários autorizados consigam exportar relatórios para análise da API.

### 🔍 Principais Funcionalidades

- **🔐 Autenticação OAuth2 / JWT**: O backend é inteiramente protegido por tokens de sessão.
- **🚨 Detecção de Ameaças**: Identifica acessos de força bruta e comportamentos de ataque.
- **🌍 Mapeamento Geográfico**: Integração gráfica com mapa-múndi e geolocalização dos IPs evasivos.
- **📊 Inteligência de Risco**: Sistema de classificação baseada no histórico de atividade local (Alto/Médio/Baixo).
- **🌐 Pipeline REST**: Um backend em FastAPI pronto para receber cargas (`.csv`, `.json`).
- **💻 App Web Securizado**: Uma central de *Login* desenvolvida no Streamlit; os painéis só carregam mediante à verificação bem-sucedida das chaves e repassam o Bearer Token por baixo dos panos.
- **⚙️ Limpo e Desacoplado**: Repositório focado com arquivos independentes e arquitetura isolada.

---

## ⚡ Instalação Rápida

Recomenda-se utilizar um ambiente virtual (`.venv`) para rodar os pacotes de criptografia e web localmente:

```bash
# 1. Clonar o repositório
git clone https://github.com/henrilopes1/log-analyzer.git
cd log-analyzer

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar o ambiente
source .venv/Scripts/activate  # Linux/Git Bash/Mac
.venv\Scripts\activate         # Windows (CMD / PowerShell)

# 4. Instalar as dependências Core, Segurança (bcrypt/jwt) e Front (streamlit)
pip install -r requirements.txt
pip install PyJWT passlib "bcrypt==4.0.1" python-multipart streamlit requests pandas
```

---

## 💡 Como Usar o Projeto

Para visualizar a ferramenta por completo, será preciso iniciar o **Backend (FastAPI)** para orquestrar as senhas e cálculos lógicos, e em seguida inicializar o **Frontend (Streamlit)** para renderizar a interface de manipulação.

### 1️⃣ Iniciando a API (Backend Segura)
No seu terminal 1 (com o ambiente `venv` ativo):
```bash
python run_api.py
```
A API ficará ativa em `http://127.0.0.1:8000`.

### 2️⃣ Iniciando o Dashboard Web (Interface de Login)
Abra um **segundo terminal paralelo**, ative seu virtual environment e use:
```bash
python -m streamlit run frontend/web_app.py --server.port 8503
```
*(Usamos a porta 8503 para evitar choque de portas em caches agressivos do Windows/Frontend).*

### 3️⃣ Testando o Sistema
1. Abra no navegador: `http://localhost:8503`
2. **Faça o Login** fornecido no banco de dados isolado da aplicação:
   - **Usuário:** `admin`
   - **Senha:** `senha123`
3. Após desbloquear, expanda a barra lateral lateral ("Upload de Arquivos").
4. Faça upload dos arquivos de teste, como `data/sample_firewall.csv` e `data/sample_auth.csv`.
5. Acione o botão de analisar logs e observe os gráficos de ofensores geográficos.

---

## 🔧 Arquitetura do Projeto

```text
log-analyzer/
├── data/                # Bases de dados simuladas para poder fazer os testes
├── examples/            # Exemplos de uso em Python de alto nível bruto
├── frontend/            # A interface Web - Lógica de Login e Renderização de Maps (web_app.py)
├── src/log_analyzer/    # Lógica de Backend (Servidor API, Middlewares, Hashers JWT)
├── tests/               # Testes automatizados
│
├── run_api.py           # O "botão de ligar" do seu Servidor Backend FastAPI
├── requirements.txt     # Listagem das bilbiotecas necessárias
└── README.md            # Este arquivo
```

---

## 📊 Endpoints da API

Se você for desenvolver uma integração via cURL, Postman ou afins:

- **POST `/token`** - Rota para trocar suas credenciais básicas por um Token JWT de Acesso. 
- **POST `/analyze/`** - Análise de logs _[REQUER O TOKEN NO HEADER "Authorization: Bearer <seu_token_aqui>"]_.
- **GET `/health`** - Checagem de disponibilidade limpa da CPU.

---

## 👨‍💻 Autor

**Henri Lopes**
- GitHub: [@henrilopes1](https://github.com/henrilopes1)
- LinkedIn: [Henri Lopes](https://www.linkedin.com/in/henri-de-oliveira-lopes)

<div align="center">
  <strong>🛡️ Mantenha seus logs seguros com o Log Analyzer Cyber! 🛡️</strong>
</div>
