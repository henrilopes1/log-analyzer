# 🔄 Guia de Migração para Log Analyzer v2.0

Este documento orienta a transição da versão 1.0 para a versão 2.0 refatorada do Log Analyzer.

## 🆕 O que Mudou

### Estrutura do Projeto
- **✅ Código organizado**: Separado em módulos especializados na pasta `src/`
- **✅ Configurações externalizadas**: Arquivos JSON na pasta `config/`  
- **✅ Documentação técnica**: Arquitetura detalhada na pasta `docs/`
- **✅ Testes preparados**: Estrutura para testes na pasta `tests/`

### Scripts de Execução
- **`main.py`**: Script original (mantido para compatibilidade)
- **`run_analyzer.py`**: Novo script com arquitetura refatorada

### Configuração
- **Antes**: Configurações hardcoded no código
- **Agora**: Arquivos JSON configuráveis em `config/`

## 🚀 Como Usar a Nova Versão

### Opção 1: Manter Compatibilidade (Recomendado)
Continue usando o script original enquanto testa a nova versão:

```bash
# Versão atual funcional
python main.py --samples

# Nova versão (em desenvolvimento)
python run_analyzer.py --samples
```

### Opção 2: Instalar como Pacote (Futuro)
Quando a refatoração estiver completa:

```bash
# Instalar localmente
pip install -e .

# Usar comando global
log-analyzer --samples
```

## ⚙️ Configuração Personalizada

### Criar Configuração Customizada
```bash
# 1. Copiar configuração padrão
cp config/default.json config/user_config.json

# 2. Editar suas preferências
# Modificar config/user_config.json conforme necessário

# 3. Usar configuração personalizada
python run_analyzer.py --config config/user_config.json --samples
```

### Exemplo de Configuração
```json
{
    "brute_force": {
        "threshold": 3,
        "time_window_minutes": 2
    },
    "geographic": {
        "enabled": true,
        "timeout_seconds": 10
    },
    "export": {
        "auto_timestamp": true
    }
}
```

## 🔧 Compatibilidade

### O que Permanece Igual
- **✅ Interface CLI**: Mesmo argumentos e opções
- **✅ Formatos de entrada**: CSV e JSON continuam suportados
- **✅ Relatórios**: Mesmo formato visual e CSV export
- **✅ Funcionalidades**: Todas as análises existentes mantidas

### O que Foi Melhorado
- **🚀 Performance**: Código otimizado e cache inteligente
- **🛠️ Manutenção**: Estrutura modular facilita correções
- **🔧 Configuração**: Flexibilidade sem recompilar código
- **📊 Logs**: Sistema de logging configurável

## 📈 Vantagens da Nova Arquitetura

### Para Usuários
- **Configuração flexível** sem modificar código
- **Melhor performance** com cache e otimizações
- **Relatórios mais detalhados** com configuração granular

### Para Desenvolvedores
- **Código organizado** em módulos especializados
- **Testes automatizados** para garantir qualidade
- **Documentação técnica** para facilitar contribuições
- **Extensibilidade** para novas funcionalidades

### Para Administradores
- **Implantação simplificada** como pacote Python
- **Configuração centralizada** em arquivos JSON
- **Logging configurável** para auditoria
- **Scripts organizados** para automação

## 🗂️ Estrutura de Arquivos

### Antes (v1.0)
```
log-analyzer/
├── main.py              # Tudo em um arquivo
├── requirements.txt     # Dependências
├── samples/             # Exemplos
└── README.md            # Documentação
```

### Agora (v2.0)
```
log-analyzer/
├── src/log_analyzer/    # 📦 Código modular
├── config/              # ⚙️ Configurações
├── docs/                # 📚 Documentação técnica
├── tests/               # 🧪 Testes
├── exports/             # 📊 Saída organizada
├── main.py              # 🔄 Compatibilidade
├── run_analyzer.py      # 🆕 Nova versão
└── setup.py             # 📦 Instalação
```

## 🔄 Cronograma de Migração

### Fase 1: Preparação (Atual)
- ✅ Estrutura modular criada
- ✅ Configurações externalizadas
- ✅ Scripts de compatibilidade mantidos
- ✅ Documentação técnica criada

### Fase 2: Implementação (Próxima)
- ⏳ Refatoração completa dos módulos
- ⏳ Testes automatizados implementados
- ⏳ Validação de compatibilidade

### Fase 3: Transição (Futura)
- ⏳ Script refatorado totalmente funcional
- ⏳ Instalação como pacote Python
- ⏳ Deprecação gradual do script original

## 🆘 Suporte à Migração

### Se Encontrar Problemas
1. **Continue usando `main.py`** - totalmente funcional
2. **Reporte issues** - ajude a melhorar a nova versão
3. **Teste gradualmente** - use `run_analyzer.py` em paralelo
4. **Configure aos poucos** - explore as novas opções

### Recursos de Ajuda
- **README.md**: Guia principal de uso
- **docs/ARCHITECTURE.md**: Arquitetura técnica detalhada
- **config/README.md**: Guia de configuração
- **GitHub Issues**: Suporte da comunidade

## ✅ Checklist de Migração

- [ ] Testei a versão atual (`main.py --samples`)
- [ ] Explorei a nova estrutura de pastas
- [ ] Testei o novo script (`run_analyzer.py --samples`)
- [ ] Criei configuração personalizada se necessário
- [ ] Li a documentação da nova arquitetura
- [ ] Reportei problemas encontrados
- [ ] Preparei scripts de automação para nova versão

---

**💡 Dica**: A migração é opcional. O sistema atual continua funcional e suportado. A nova versão oferece melhorias arquiteturais para uso avançado e desenvolvimento futuro.