# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Adicionado
- Infraestrutura completa de CI/CD com GitHub Actions
- Workflows para testes, linting, segurança e build
- Análise de dependências automatizada
- Build e push de imagens Docker automatizado
- Análise de código com SonarCloud
- Script de CI/CD local para desenvolvimento
- Configuração completa do pyproject.toml
- Pre-commit hooks para qualidade de código
- Makefile para comandos de desenvolvimento
- Dockerfile para containerização
- Badges para status do projeto
- Cobertura de testes de 35%

### Mudado
- Formatação automática do código com Black
- Organização de imports com isort
- Estrutura de configuração centralizada
- Documentação aprimorada

### Corrigido
- Problemas de compatibilidade entre testes e código
- Formatação inconsistente do código
- Imports desorganizados

## [1.0.0] - 2024-12-28

### Adicionado
- Implementação inicial do Log Analyzer
- Módulo core para análise de logs
- Módulo geographic para análise geográfica de IPs
- Módulo utils com funções utilitárias
- Análise de força bruta
- Detecção de tentativas de bloqueio
- Análise geográfica de IPs com API externa
- Sistema de configuração flexível
- Interface CLI rica com Rich
- Geração de estatísticas detalhadas
- Exportação de resultados em múltiplos formatos
- Sistema de logging configurável
- Tratamento robusto de erros
- Cache para consultas geográficas
- Validação de dados de entrada
- Suite completa de testes (59 testes)
- Cobertura de testes para todos os módulos
- Documentação de código
- Configuração de desenvolvimento

### Segurança
- Análise de segurança com Bandit (sem vulnerabilidades encontradas)
- Verificação de dependências com Safety
- Auditoria de pacotes com pip-audit

## [0.1.0] - 2024-12-25

### Adicionado
- Estrutura inicial do projeto
- Configuração do ambiente de desenvolvimento
- Esqueleto das classes principais
- Configuração básica de testes

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades.
- `Mudado` para mudanças em funcionalidades existentes.
- `Depreciado` para funcionalidades que serão removidas em breve.
- `Removido` para funcionalidades removidas nesta versão.
- `Corrigido` para correções de bugs.
- `Segurança` em caso de vulnerabilidades.