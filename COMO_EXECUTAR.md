# 🚀 LOG ANALYZER - GUIA DE EXECUÇÃO

## 📋 COMO EXECUTAR O PROJETO

### 1. 🔥 Iniciar API (Modo Principal)
```bash
cd "c:\Users\Henri\OneDrive - SENAC - SP\Área de Trabalho\Projetos CYBER\log-analyzer"
python src/log_analyzer/run_api.py
```

**✅ Resultado:** API rodando em http://127.0.0.1:8000

### 2. 🌐 Acessar Interface Web
- **Aplicação:** http://127.0.0.1:8000
- **Documentação Interativa:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health
- **Métricas:** http://127.0.0.1:8000/metrics

### 3. 📤 Testar Upload de Arquivo
1. Vá para http://127.0.0.1:8000/docs
2. Clique em "POST /analyze/"
3. Clique em "Try it out"
4. Faça upload de um arquivo CSV de logs
5. Clique em "Execute"

### 4. 🧪 Executar Testes
```bash
# Teste funcional completo
python test_functional.py

# Teste de performance
python test_performance.py

# Demonstração completa
python demo_project.py
```

### 5. 🏃‍♂️ Execução Rápida via CLI
```bash
# Análise direta de arquivo
python src/log_analyzer/main.py --file data/sample_firewall_logs.csv

# Análise com saída JSON
python src/log_analyzer/main.py --file data/sample_firewall_logs.csv --output json
```

## 📊 STATUS ATUAL

✅ **FUNCIONANDO:**
- API REST completa
- Interface web interativa
- Sistema de upload de arquivos
- Análise de força bruta
- Análise geográfica
- Sistema de cache
- Monitoramento de performance
- Health checks
- Documentação automática

⚡ **PERFORMANCE:**
- Cache híbrido (Memory + Redis)
- Processamento assíncrono
- Logs estruturados
- Métricas em tempo real

🔧 **COMPONENTES:**
- FastAPI + Uvicorn
- Pandas para análise
- Requests para APIs
- Sistema de configuração avançado
- Logging estruturado

## 🎯 PRÓXIMOS PASSOS

1. **Execute a API:** `python src/log_analyzer/run_api.py`
2. **Acesse:** http://127.0.0.1:8000/docs
3. **Teste upload:** Use interface web para upload de CSV
4. **Monitore:** Verifique métricas e health checks

## 📝 EXEMPLO DE ARQUIVO CSV

```csv
timestamp,source_ip,destination_ip,action,status_code,bytes_transferred
2024-01-01 10:00:00,192.168.1.100,8.8.8.8,allow,200,1024
2024-01-01 10:00:30,192.168.1.100,8.8.8.8,block,403,0
2024-01-01 10:01:00,192.168.1.100,8.8.8.8,allow,200,2048
```

## 🆘 PROBLEMAS COMUNS

**❌ "ModuleNotFoundError":**
```bash
# Instalar dependências
pip install -r requirements.txt
```

**❌ "Port already in use":**
```bash
# Parar processos na porta 8000
taskkill /f /im python.exe
```

**❌ "logs directory not found":**
```bash
# Criar diretório de logs
mkdir logs
```

---
🎉 **PROJETO 100% FUNCIONAL!**