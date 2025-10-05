# 🧪 Testes da API Log Analyzer

Este diretório contém testes unitários e de integração abrangentes para a API Log Analyzer, utilizando pytest e requests.

## 📋 Estrutura dos Testes

```
tests/
├── conftest.py          # Configurações e fixtures globais do pytest
├── test_api.py          # Testes principais da API
└── README.md           # Este arquivo
```

## 🎯 Cenários de Teste Cobertos

### ✅ Endpoints de Saúde e Status
- **`test_api_status_endpoint`**: Verifica se o endpoint `/` retorna status correto
- **`test_health_endpoint_returns_healthy`**: Testa se `/health` retorna status "healthy"
- **`test_api_info_endpoint`**: Valida se `/api-info` retorna informações da API
- **`test_metrics_endpoint`**: Verifica se `/metrics` retorna métricas válidas

### 📤 Testes de Upload e Análise
- **`test_analyze_no_files_returns_400`**: Erro 400 quando nenhum arquivo é enviado
- **`test_analyze_with_firewall_log_success`**: Upload bem-sucedido de arquivo de firewall
- **`test_analyze_with_auth_log_success`**: Upload bem-sucedido de arquivo de autenticação
- **`test_analyze_with_both_logs_success`**: Upload de ambos os arquivos
- **`test_analyze_with_unsupported_format_returns_400`**: Erro 400 para formato não suportado
- **`test_analyze_with_malformed_csv_returns_400`**: Tratamento de CSV malformado

### ⚡ Testes de Performance
- **`test_api_response_time`**: API responde em menos de 2 segundos
- **`test_health_check_response_time`**: Health check responde em menos de 1 segundo
- **`test_concurrent_requests`**: Suporte a requisições concorrentes

### 🛡️ Testes de Tratamento de Erros
- **`test_nonexistent_endpoint_returns_404`**: Endpoint inexistente retorna 404
- **`test_invalid_method_returns_405`**: Método HTTP inválido retorna 405
- **`test_large_file_upload_handling`**: Tratamento de arquivos grandes

## 🚀 Como Executar os Testes

### Pré-requisitos

1. **Instalar dependências:**
   ```bash
   pip install pytest requests
   ```

2. **Iniciar a API:**
   ```bash
   python src/log_analyzer/main.py
   ```
   A API deve estar rodando em `http://127.0.0.1:8000`

### Métodos de Execução

#### 1. 🎯 Execução Básica
```bash
# Executar todos os testes
pytest tests/

# Executar apenas test_api.py
pytest tests/test_api.py

# Execução verbosa
pytest tests/ -v
```

#### 2. 🔧 Usando o Script Personalizado
```bash
# Executar todos os testes
python scripts/run_tests.py

# Executar com saída verbosa
python scripts/run_tests.py -v

# Executar apenas testes de integração
python scripts/run_tests.py -m integration

# Executar testes que contenham "health"
python scripts/run_tests.py -k "health"

# Executar com relatório de cobertura
python scripts/run_tests.py --coverage
```

#### 3. 🎨 Execução Direta do Arquivo
```bash
# Executar test_api.py diretamente
python tests/test_api.py
```

### 🏷️ Marcadores de Teste

Os testes são organizados com marcadores para execução seletiva:

- **`integration`**: Testes de integração com a API
- **`slow`**: Testes que podem ser lentos (upload de arquivos)
- **`performance`**: Testes de performance

```bash
# Executar apenas testes rápidos (excluir lentos)
pytest -m "not slow"

# Executar apenas testes de performance
pytest -m performance
```

## 📊 Configuração Personalizada

### Variáveis de Ambiente

- **`API_BASE_URL`**: URL base da API (default: `http://127.0.0.1:8000`)

```bash
# Testar contra API em porta diferente
export API_BASE_URL=http://127.0.0.1:8080
pytest tests/
```

### Arquivo pytest.ini

O arquivo `pytest.ini` contém configurações padrão:
- Timeout de 300 segundos
- Saída colorida
- Marcadores customizados
- Diretórios de teste

## 📈 Relatórios de Cobertura

Para gerar relatórios de cobertura de código:

```bash
# Instalar pytest-cov
pip install pytest-cov

# Executar testes com cobertura
pytest --cov=src/log_analyzer --cov-report=html --cov-report=term

# Ou usar o script personalizado
python scripts/run_tests.py --coverage
```

## 🔄 Execução Paralela

Para executar testes em paralelo (mais rápido):

```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Executar em paralelo
pytest -n auto

# Ou usar o script personalizado
python scripts/run_tests.py --parallel
```

## 🐛 Solução de Problemas

### API não está disponível
```
⚠️ API não está acessível em http://127.0.0.1:8000
💡 Certifique-se de que a API está rodando antes de executar os testes
```

**Solução:**
1. Verificar se a API está rodando: `curl http://127.0.0.1:8000/health`
2. Iniciar a API: `python src/log_analyzer/main.py`
3. Verificar se a porta 8000 está livre

### Testes de timeout
```
FAILED tests/test_api.py::TestFileAnalysis::test_analyze_with_firewall_log_success - requests.exceptions.Timeout
```

**Solução:**
1. Aumentar timeout: `pytest --timeout=600`
2. Verificar performance da API
3. Usar arquivos menores para teste

### Dependências faltando
```
ModuleNotFoundError: No module named 'pytest'
```

**Solução:**
```bash
pip install pytest requests pytest-cov pytest-xdist
```

## 📝 Exemplos de Uso

### Teste Específico
```bash
# Testar apenas o endpoint de health
pytest tests/test_api.py::TestAPIHealth::test_health_endpoint_returns_healthy -v
```

### Execução com Filtros
```bash
# Testar apenas uploads de arquivo
pytest -k "upload or firewall or auth" -v

# Excluir testes lentos
pytest -m "not slow" -v
```

### Debug de Teste Específico
```bash
# Executar com máximo de detalhes
pytest tests/test_api.py::TestFileAnalysis::test_analyze_no_files_returns_400 -vvv --tb=long
```

## 🎉 Validação Completa

Para validar completamente a API:

```bash
# Execução completa com relatórios
python scripts/run_tests.py --coverage --verbose

# Verificar se todos os cenários passam
pytest tests/ -v --tb=short
```

Os testes garantem que todos os cenários solicitados estão funcionando:
- ✅ `/health` retorna status "healthy"
- ✅ `/api-info` retorna informações da API
- ✅ `/analyze/` com upload bem-sucedido
- ✅ `/analyze/` sem arquivos retorna erro 400
- ✅ `/analyze/` com formato não suportado retorna erro 400