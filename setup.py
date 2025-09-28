"""
Setup script para o Log Analyzer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler README para descrição longa
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Ler requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    requirements = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name="log-analyzer",
    version="2.0.0",
    author="Security Team",
    author_email="security@company.com",
    description="Ferramenta avançada para análise de logs de segurança",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/company/log-analyzer",
    
    # Pacotes
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Dependências
    install_requires=requirements,
    
    # Extras
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.5.0",
        ]
    },
    
    # Classificadores PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Logging",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Versão mínima do Python
    python_requires=">=3.8",
    
    # Scripts de linha de comando
    entry_points={
        "console_scripts": [
            "analyzer=log_analyzer.main:main",
            "log-analyzer=log_analyzer.main:main",
        ],
    },
    
    # Arquivos de dados
    package_data={
        "log_analyzer": [
            "config/*.json",
            "samples/*.csv",
            "samples/*.json",
        ],
    },
    
    # Keywords para PyPI
    keywords=[
        "security", "log-analysis", "cybersecurity", 
        "brute-force", "port-scan", "geolocation",
        "firewall", "authentication", "monitoring"
    ],
    
    # Metadata do projeto
    project_urls={
        "Bug Reports": "https://github.com/company/log-analyzer/issues",
        "Source": "https://github.com/company/log-analyzer",
        "Documentation": "https://log-analyzer.readthedocs.io/",
        "Changelog": "https://github.com/company/log-analyzer/blob/main/CHANGELOG.md",
    },
    
    # Incluir arquivos não-Python
    include_package_data=True,
    
    # Zip safe
    zip_safe=False,
)