# Guia de Testes do Log Analyzer

## 🧪 Como Testar o Projeto

### 1. Testes Unitários Automatizados
```bash
# Instalar dependências de teste
pip install -r requirements-dev.txt

# Executar todos os testes
python -m pytest tests/ -v

# Executar com cobertura
python -m pytest tests/ -v --cov=src --cov-report=html

# Executar testes específicos
python -m pytest tests/test_core.py -v
```

### 2. Testes Funcionais Rápidos
```bash
# Script personalizado de teste
python test_functional.py
```

### 3. Teste Manual das Funcionalidades

#### A. Testando o Core (Análise de Logs)
```python
from src.log_analyzer.core import LogAnalyzer
import pandas as pd

# Criar dados de teste
data = pd.DataFrame({
    'timestamp': ['2024-01-01 10:00:00', '2024-01-01 10:01:00'],
    'source_ip': ['192.168.1.100', '192.168.1.100'],
    'destination_ip': ['8.8.8.8', '8.8.8.8'],
    'action': ['allow', 'block'],
    'status_code': [200, 403]
})

# Inicializar analyzer
analyzer = LogAnalyzer()
analyzer.data = data

# Executar análises
brute_force = analyzer.analyze_brute_force()
stats = analyzer.generate_statistics()

print(f"Força bruta detectada: {len(brute_force)}")
print(f"Estatísticas: {stats}")
```

#### B. Testando Análise Geográfica
```python
from src.log_analyzer.geographic import GeographicAnalyzer

geo = GeographicAnalyzer()

# Testar IP público
location = geo.get_ip_location("8.8.8.8")
print(f"Localização de 8.8.8.8: {location}")

# Analisar múltiplos IPs
ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
analysis = geo.analyze_ips(ips)
print(f"Análise geográfica: {analysis}")
```

#### C. Testando a API
```python
# Iniciar servidor API
python run_api.py

# Em outro terminal, testar endpoints:
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/api-info
```

### 4. Teste com Arquivos Reais

#### Criar arquivo CSV de exemplo:
```csv
timestamp,source_ip,destination_ip,action,status_code
2024-01-01 10:00:00,192.168.1.100,8.8.8.8,allow,200
2024-01-01 10:01:00,192.168.1.100,8.8.8.8,block,403
2024-01-01 10:02:00,10.0.0.50,1.1.1.1,allow,200
```

#### Testar carregamento:
```python
from src.log_analyzer.core import LogAnalyzer

analyzer = LogAnalyzer("exemplo.csv")
data = analyzer.load_data("exemplo.csv")
print(f"Dados carregados: {len(data)} linhas")
```

### 5. Testes de Build e Deploy

#### Build do Pacote:
```bash
# Build
python -m build

# Verificar dist/
ls dist/

# Validar pacote
twine check dist/*
```

#### Teste de Instalação:
```bash
# Instalar localmente
pip install dist/*.whl

# Testar CLI
log-analyzer --help
```

### 6. Testes de Qualidade

#### Formatação:
```bash
black --check src/
isort --check-only src/
```

#### Linting:
```bash
flake8 src/ --max-line-length=88
```

#### Segurança:
```bash
bandit -r src/
safety check
```

#### Tipos:
```bash
mypy src/
```

### 7. Testes de Performance

```python
import time
from src.log_analyzer.core import LogAnalyzer
import pandas as pd

# Criar dataset grande
large_data = pd.DataFrame({
    'timestamp': ['2024-01-01 10:00:00'] * 10000,
    'source_ip': ['192.168.1.100'] * 10000,
    'destination_ip': ['8.8.8.8'] * 10000,
    'action': ['allow'] * 10000,
    'status_code': [200] * 10000
})

analyzer = LogAnalyzer()
analyzer.data = large_data

start = time.time()
stats = analyzer.generate_statistics()
end = time.time()

print(f"Tempo para 10k linhas: {end - start:.2f}s")
```

### 8. Testes de Integração

#### Docker:
```bash
# Build imagem
docker build -t log-analyzer .

# Executar container
docker run -p 8000:8000 log-analyzer

# Testar API
curl http://localhost:8000/health
```

#### GitHub Actions:
```bash
# Simular CI/CD localmente
act -j test-and-build
```

## 🎯 Critérios de Aprovação

### ✅ Essenciais (80%+ para aprovação):
- [x] Testes unitários passando
- [x] Core functionality funcionando
- [x] API importável
- [x] Build do pacote OK
- [x] Análise geográfica funcional

### 🚀 Opcionais (100% para excelência):
- [ ] Todos os linters passando
- [ ] 90%+ cobertura de testes
- [ ] Performance otimizada
- [ ] Documentação completa
- [ ] Deploy automatizado

## 📊 Status Atual: ✅ APROVADO (80%)

O projeto está funcional e pronto para uso básico!