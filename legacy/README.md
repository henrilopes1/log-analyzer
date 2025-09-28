# Legacy - Versão Original do Log Analyzer

Esta pasta contém a versão original (v1.0) do Log Analyzer, mantida para compatibilidade e referência.

## Arquivo Legado

### `main_legacy.py`
- **Descrição**: Script original completo e funcional do Log Analyzer v1.0
- **Status**: ✅ Totalmente funcional
- **Uso**: Para compatibilidade ou comparação com a nova versão
- **Características**: Código monolítico com todas as funcionalidades em um arquivo

## Como Usar a Versão Legacy

```bash
# Executar a versão original
python legacy/main_legacy.py --samples

# Com análise geográfica
python legacy/main_legacy.py --samples

# Exportar resultados
python legacy/main_legacy.py --samples --export-csv legacy_report.csv
```

## Diferenças Entre as Versões

### Versão Legacy (v1.0)
- ✅ Código em um único arquivo
- ✅ Configurações hardcoded
- ✅ Funcional e estável
- ✅ Análise geográfica integrada

### Versão Refatorada (v2.0)
- 🆕 Arquitetura modular
- 🆕 Configurações externalizadas
- 🆕 Melhor manutenibilidade
- 🆕 Estrutura para testes
- 🆕 Documentação técnica

## Quando Usar a Versão Legacy

1. **Compatibilidade**: Se a nova versão apresentar problemas
2. **Referência**: Para comparar comportamentos
3. **Desenvolvimento**: Para verificar implementações originais
4. **Produção**: Como fallback se necessário

## Migração Recomendada

Recomendamos migrar para a nova versão refatorada:
```bash
# Nova versão (recomendada)
python main.py --samples
```

A versão legacy será mantida para garantir continuidade, mas o desenvolvimento futuro focará na versão refatorada.