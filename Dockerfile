# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

# Instalar dependências do sistema necessárias para build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt requirements-dev.txt ./

# Criar ambiente virtual e instalar dependências
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Estágio final da imagem
FROM python:3.11-slim

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar apenas dependências mínimas de runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar ambiente virtual do estágio builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Definir diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY src/ src/
COPY tests/ tests/
COPY pyproject.toml Makefile ./

# Criar diretórios necessários
RUN mkdir -p logs exports samples && \
    chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Instalar o pacote em modo desenvolvimento
RUN pip install -e .

# Definir variáveis de ambiente
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expor porta para possível interface web futura
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import log_analyzer; print('OK')" || exit 1

# Labels para metadados
LABEL maintainer="henri@example.com"
LABEL version="1.0.0"
LABEL description="Advanced log analysis tool for cybersecurity"
LABEL org.opencontainers.image.source="https://github.com/henrilopes1/log-analyzer"

# Comando padrão
CMD ["python", "-m", "log_analyzer.cli", "--help"]