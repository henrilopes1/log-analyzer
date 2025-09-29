# 🚀 Guia Rápido da API Log Analyzer

## 📋 Pré-requisitos

```bash
# Instalar dependências da API
pip install fastapi uvicorn[standard] requests

# Verificar instalação
pip show fastapi uvicorn
```

## 🌐 Executar o Servidor da API

### Opção 1: Script de inicialização
```bash
# Desenvolvimento (com reload automático)
python run_api.py --reload --debug

# Produção (host externo)
python run_api.py --prod --host 0.0.0.0
```

### Opção 2: Diretamente com uvicorn
```bash
# Desenvolvimento
uvicorn src.log_analyzer.api:app --reload --host 127.0.0.1 --port 8000

# Produção
uvicorn src.log_analyzer.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Opção 3: Make commands
```bash
# Instalar dependências da API
make api-install

# Servidor de desenvolvimento
make api-dev

# Servidor de produção
make api-prod

# Testes da API
make api-test

# Demo completa
make api-demo
```

## 🔗 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Status da API |
| `/health` | GET | Health check |
| `/analyze/` | POST | Análise de logs (upload de arquivos) |
| `/api-info` | GET | Informações da API |
| `/docs` | GET | Documentação Swagger UI |
| `/redoc` | GET | Documentação ReDoc |

## 📤 Testando a API

### 1. Status da API
```bash
# Testar se a API está rodando
curl http://127.0.0.1:8000/

# Resposta esperada:
# {"status": "Log Analyzer API is running"}
```

### 2. Health Check
```bash
curl http://127.0.0.1:8000/health

# Resposta esperada:
# {"status": "healthy", "version": "1.0.0", "service": "log-analyzer-api"}
```

### 3. Análise de Logs
```bash
# Upload de um arquivo
curl -X POST "http://127.0.0.1:8000/analyze/" \
  -F "firewall_log=@data/sample_firewall.csv"

# Upload de dois arquivos
curl -X POST "http://127.0.0.1:8000/analyze/" \
  -F "firewall_log=@data/sample_firewall.csv" \
  -F "auth_log=@data/sample_auth.csv"
```

### 4. Usando o cliente Python
```bash
# Testar status
python examples/api_client_example.py --test-status

# Criar dados de exemplo
python examples/api_client_example.py --create-samples

# Analisar logs
python examples/api_client_example.py --analyze data/sample_firewall.csv

# Obter informações da API
python examples/api_client_example.py --info
```

## 🧪 Testes Automatizados

```bash
# Executar testes da API (servidor deve estar rodando)
python tests/test_api.py

# Testes específicos com URL personalizada
python tests/test_api.py --url http://127.0.0.1:8000
```

## 🐳 Docker

### Docker Compose (Recomendado)
```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f log-analyzer-api

# Parar serviços
docker-compose down
```

### Docker standalone
```bash
# Construir imagem
docker build -f Dockerfile.api -t log-analyzer-api .

# Executar container
docker run -d \
  --name log-analyzer-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data:ro \
  log-analyzer-api

# Verificar logs do container
docker logs log-analyzer-api

# Parar container
docker stop log-analyzer-api
```

## 📊 Formato de Resposta da Análise

```json
{
  "summary": {
    "files_processed": 2,
    "total_events": 20,
    "analysis_completed": true
  },
  "firewall_analysis": [
    {
      "timestamp": "2024-01-01 10:00:02",
      "source_ip": "203.0.113.5",
      "destination_ip": "10.0.0.1",
      "port": 22,
      "protocol": "TCP",
      "action": "DENY"
    }
  ],
  "brute_force_attacks": [
    {
      "ip": "203.0.113.5",
      "attempts": 7,
      "risk_level": "high"
    }
  ],
  "geographic_analysis": [
    {
      "ip": "203.0.113.5",
      "country": "United States",
      "region": "California",
      "city": "Los Angeles"
    }
  ],
  "top_suspicious_ips": [
    {
      "ip": "203.0.113.5",
      "occurrences": 7
    }
  ],
  "alerts": {
    "high_risk": [
      {
        "ip": "203.0.113.5",
        "occurrences": 7
      }
    ],
    "medium_risk": [],
    "low_risk": []
  },
  "statistics": {
    "total_connections": 20,
    "denied_connections": 7,
    "allowed_connections": 13,
    "unique_ips": 4
  },
  "metadata": {
    "api_version": "1.0.0",
    "analyzer_version": "1.0.0",
    "files_uploaded": ["sample_firewall.csv", "sample_auth.csv"]
  }
}
```

## 🌐 Acesso à Documentação

Após iniciar o servidor, acesse:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔧 Configurações Avançadas

### Variáveis de Ambiente
```bash
# Configurar porta
export API_PORT=8080

# Configurar host
export API_HOST=0.0.0.0

# Modo de produção
export API_ENV=production
```

### Nginx Proxy (Opcional)
```bash
# Usar com nginx (requires profile)
docker-compose --profile with-nginx up -d
```

## ⚠️ Troubleshooting

### Problema: "Python não encontrado"
```bash
# Verificar Python instalado
python --version
python3 --version

# Usar python3 se necessário
python3 run_api.py --reload
```

### Problema: "Módulo não encontrado"
```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar PYTHONPATH
export PYTHONPATH=$(pwd)/src
```

### Problema: "Porta já em uso"
```bash
# Usar porta diferente
python run_api.py --port 8080

# Ou verificar processos usando a porta
netstat -an | findstr 8000  # Windows
lsof -i :8000               # Linux/Mac
```

## 📧 Suporte

Para problemas ou dúvidas:
1. Verificar documentação em `/docs`
2. Executar testes: `python tests/test_api.py`
3. Verificar logs do servidor
4. Criar issue no repositório GitHub

---

✅ **API Log Analyzer pronta para uso!** 🛡️