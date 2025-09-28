# Configuração do Log Analyzer

Esta pasta contém arquivos de configuração para personalizar o comportamento do Log Analyzer.

## Arquivos de Configuração

### `default.json`
Configurações padrão do sistema. Não modifique este arquivo diretamente.

### `user_config.json` (opcional)
Configurações personalizadas do usuário. Crie este arquivo para sobrescrever configurações padrão.

### `local_config.json` (opcional)  
Configurações específicas do ambiente local. Este arquivo é ignorado pelo Git.

## Exemplo de Configuração Personalizada

Crie um arquivo `user_config.json` com o seguinte formato:

```json
{
    "brute_force": {
        "threshold": 3,
        "time_window_minutes": 2
    },
    "port_scan": {
        "threshold": 5,
        "time_window_minutes": 1
    },
    "geographic": {
        "enabled": true,
        "timeout_seconds": 10,
        "high_risk_countries": ["CN", "RU", "KP", "IR", "BY", "TR"]
    },
    "risk_classification": {
        "high_threshold": 15,
        "medium_threshold": 8
    },
    "export": {
        "auto_timestamp": true,
        "default_filename": "security_analysis.csv"
    }
}
```

## Uso

Para usar uma configuração personalizada:

```bash
python run_analyzer.py --config config/user_config.json --samples
```