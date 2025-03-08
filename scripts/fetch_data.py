import requests
import json
import os
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/fetch.log'),
        logging.StreamHandler()
    ]
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def obter_dados_api(url):
    """Obtém dados da API com retry mechanism"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
# Diretório para armazenar os dados
DATA_DIR = 'data'
HISTORICO_DIR = os.path.join(DATA_DIR, 'historico')

# Garantir que os diretórios existam
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HISTORICO_DIR, exist_ok=True)

def obter_dados_fiis(tickers):
    """Obtém dados detalhados dos FIIs especificados"""
    try:
        dados_fiis = []
        for ticker in tickers:
            url = f"https://brapi.dev/api/quote/{ticker}?fundamental=true"
            dados = obter_dados_api(url)
            if dados and 'results' in dados:
                dados_fiis.append(dados['results'][0])
        
        return dados_fiis
    except Exception as e:
        logging.error(f"Erro ao obter dados dos FIIs: {e}")
        return []

def salvar_dados(dados, nome_arquivo='fiis.json'):
    """Salva os dados em formato JSON"""
    try:
        caminho_arquivo = os.path.join(DATA_DIR, nome_arquivo)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({
                'atualizacao': datetime.now().isoformat(),
                'fiis': dados
            }, f, ensure_ascii=False, indent=2)
        logging.info(f"Dados salvos em {caminho_arquivo}")
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")

def main():
    # Obter todos os FIIs disponíveis
    todos_fiis = obter_lista_fiis()
    
    # Extrair apenas os tickers
    tickers = [fii['stock'] for fii in todos_fiis]
    
    # Obter dados detalhados (em lotes de 20 para não sobrecarregar a API)
    todos_dados = []
    for i in range(0, len(tickers), 20):
        lote = tickers[i:i+20]
        dados_lote = obter_dados_fiis(lote)
        todos_dados.extend(dados_lote)
    
    # Filtrar FIIs com preço abaixo de R$ 25,00
    fiis_filtrados = [fii for fii in todos_dados if fii.get('regularMarketPrice', 0) < 25.0]
    
    # Salvar dados
    salvar_dados({'atualizacao': datetime.now().isoformat(), 'fiis': fiis_filtrados})

if __name__ == "__main__":
    main()
