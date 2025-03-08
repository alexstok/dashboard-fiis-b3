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

def obter_lista_fiis():
    """Obtém a lista de todos os FIIs disponíveis na B3"""
    try:
        # Usando a API brapi.dev que é gratuita
        url = "https://brapi.dev/api/quote/list?type=fii&sortBy=name&sortOrder=asc"
        response = requests.get(url)
        data = response.json()
        
        # Filtrar apenas os FIIs
        fiis = [item for item in data['stocks'] if item['stock'].endswith('11')]
        
        print(f"Encontrados {len(fiis)} FIIs na B3")
        return fiis
    except Exception as e:
        print(f"Erro ao obter lista de FIIs: {e}")
        return []

def obter_dados_fiis(tickers):
    """Obtém dados detalhados dos FIIs especificados"""
    try:
        # Converter lista de tickers para string separada por vírgula
        tickers_str = ','.join(tickers)
        
        # Obter cotações atuais
        url = f"https://brapi.dev/api/quote/{tickers_str}?fundamental=true&dividends=true"
        response = requests.get(url)
        data = response.json()
        
        print(f"Dados obtidos para {len(data['results'])} FIIs")
        return data['results']
    except Exception as e:
        print(f"Erro ao obter dados dos FIIs: {e}")
        return []

def salvar_dados(dados, nome_arquivo='fiis.json'):
    """Salva os dados em um arquivo JSON"""
    try:
        # Salvar arquivo principal
        caminho_arquivo = os.path.join(DATA_DIR, nome_arquivo)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        # Salvar cópia no histórico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        caminho_historico = os.path.join(HISTORICO_DIR, f'fiis_{timestamp}.json')
        with open(caminho_historico, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"Dados salvos em {caminho_arquivo} e {caminho_historico}")
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

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
