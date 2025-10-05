# Scripts de Desenvolvimento e Utilidades

Esta pasta contém scripts auxiliares para desenvolvimento, testes e demonstrações do Log Analyzer.

# Scripts de Desenvolvimento e Utilidades

Esta pasta contém scripts auxiliares especializados para desenvolvimento, performance e CI/CD do Log Analyzer.

## 📁 Estrutura dos Scripts

### ⚡ **Scripts de Performance**

#### `test_performance.py`
- **Propósito:** Testes de performance e benchmarking avançado
- **Uso:** `python scripts/test_performance.py`
- **Características:** 
  - Métricas de tempo, memória e escalabilidade
  - Geração de datasets grandes com NumPy
  - Profiling detalhado com psutil
  - Relatórios de performance especializados

### 🔄 **Scripts de Pipeline**

#### `test_pipeline.py`
- **Propósito:** Simulação completa de pipeline release
- **Uso:** `python scripts/test_pipeline.py`
- **Características:** 
  - Simulação de workflow GitHub Actions
  - Validação de build e release localmente
  - Testes de integração de pipeline

### 🚀 **Scripts de Execução**

#### `run_tests.py`
- **Propósito:** Executor central para todos os tipos de teste
- **Uso:** `python scripts/run_tests.py [opções]`
- **Características:** 
  - Múltiplas opções de configuração
  - Suporte a pytest com argumentos customizados
  - Verificação automática de dependências
  - Interface unificada para todos os testes

### 🔄 **Scripts de CI/CD**

#### `ci_cd_local.py`
- **Propósito:** Simulação local completa do pipeline CI/CD
- **Uso:** `python scripts/ci_cd_local.py`
- **Características:** 
  - Execução de todos os tipos de teste
  - Validação de qualidade de código
  - Relatórios consolidados
  - Simulação do ambiente GitHub Actions

## 📋 Como Usar

### Executar Testes Formais (Recomendado)
```bash
# Usar pytest diretamente para testes robustos
python -m pytest tests/ -v

# Executor unificado com opções avançadas
python scripts/run_tests.py --coverage --verbose
```

### Executar Scripts Especializados
```bash
# Testes de performance e benchmarking
python scripts/test_performance.py

# Simulação de pipeline release
python scripts/test_pipeline.py

# Pipeline CI/CD completo
python scripts/ci_cd_local.py
```

### Executar com Opções Avançadas
```bash
# Com cobertura e paralelo
python scripts/run_tests.py --coverage --parallel

# Com marcadores específicos
python scripts/run_tests.py -m "integration"

# Com timeout personalizado
python scripts/run_tests.py --timeout 600
```

## 🎯 Diferenças Entre Scripts

| Script | Propósito | Executar Quando | Saída |
|--------|-----------|-----------------|-------|
| `tests/test_*.py` | Testes formais unitários | Durante desenvolvimento | Pytest profissional |
| `scripts/test_performance.py` | Benchmarking especializado | Otimizações de performance | Métricas detalhadas |
| `scripts/test_pipeline.py` | Simulação release | Validação de release | Pipeline completo |
| `scripts/run_tests.py` | Orquestração de testes | Validação geral | Configurável |
| `scripts/ci_cd_local.py` | Simulação CI/CD completa | Antes de commits | Pipeline completo |

## 🚨 Requisitos

### Dependências Básicas
```bash
pip install pytest requests pandas numpy
```

### Dependências Opcionais
```bash
# Para testes paralelos
pip install pytest-xdist

# Para cobertura
pip install pytest-cov

# Para performance
pip install psutil
```

## 📝 Convenções

- **Scripts de teste** começam com `test_`
- **Scripts de execução** começam com `run_`
- **Scripts de CI/CD** contêm `ci_cd` no nome
- Todos os scripts são executáveis e auto-documentados
- Saída formatada com emojis e cores para melhor UX

## 🔧 Manutenção

- Scripts são independentes dos testes formais em `tests/`
- Podem ser modificados sem afetar o pipeline principal
- Devem ser mantidos atualizados com novas funcionalidades
- Documentação deve ser atualizada quando novos scripts forem adicionados

---

💡 **Dica:** Use `python scripts/run_tests.py --help` para ver todas as opções disponíveis.