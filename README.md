# Dashboard de Análise de FIIs da B3

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/seu-usuario/dashboard-fiis-b3/update-dashboard.yml?label=dashboard)
![GitHub last commit](https://img.shields.io/github/last-commit/seu-usuario/dashboard-fiis-b3)

// ...existing code...

## Instalação Local

### Pré-requisitos
- Python 3.9+
- pip
- Git

### Configuração
```bash
# Clonar e configurar
git clone https://github.com/seu-usuario/dashboard-fiis-b3.git
cd dashboard-fiis-b3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Executar localmente
python scripts/fetch_data.py
python scripts/process_data.py
python scripts/update_dashboard.py
```