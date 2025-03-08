import requests
import json
import os
import time
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Definir diretórios
DATA_DIR = 'data'
HISTORICO_DIR = os.path.join(DATA_DIR, 'historico')

# Criar diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HISTORICO_DIR, exist_ok=True)

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv('API_KEY')
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '0.5'))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(DATA_DIR, 'fetch.log')),
        logging.StreamHandler()
    ]
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def obter_dados_api(url):
    """Obtém dados da API com retry mechanism"""
    try:
        headers = {'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição: {e}")
        raise

# ...existing code...

def obter_dados_fiis(tickers):
    """Obtém dados detalhados dos FIIs especificados"""
    try:
        dados_fiis = []
        total_tickers = len(tickers)
        
        for i, ticker in enumerate(tickers, 1):
            logging.info(f"Obtendo dados do FII {ticker} ({i}/{total_tickers})")
            url = f"https://brapi.dev/api/quote/{ticker}?fundamental=true"
            
            try:
                dados = obter_dados_api(url)
                
                if dados and 'results' in dados and dados['results']:
                    fii = dados['results'][0]
                    if validar_dados_fii(fii):
                        dados_fiis.append(fii)
                    else:
                        logging.warning(f"Dados incompletos para {ticker}")
                else:
                    logging.warning(f"Sem dados para {ticker}")
                
                # Rate limiting
                time.sleep(RATE_LIMIT_DELAY)
                
            except Exception as e:
                logging.error(f"Erro ao processar {ticker}: {e}")
                continue
            
        return dados_fiis
    except Exception as e:
        logging.error(f"Erro ao obter dados dos FIIs: {e}")
        return []

# ...existing code...

def main():
    try:
        logging.info("Iniciando coleta de dados...")
        
        if not API_KEY:
            logging.warning("API_KEY não configurada. Algumas funcionalidades podem ser limitadas.")
        
        # Obter todos os FIIs disponíveis
        todos_fiis = obter_lista_fiis()
        
        if not todos_fiis:
            raise ValueError("Nenhum FII encontrado")
        
        # Extrair apenas os tickers
        tickers = [fii['stock'] for fii in todos_fiis]
        logging.info(f"Encontrados {len(tickers)} FIIs")
        
        # Obter dados detalhados (em lotes de 20)
        todos_dados = []
        total_lotes = (len(tickers) + 19) // 20  # Arredonda para cima
        
        for i in range(0, len(tickers), 20):
            lote = tickers[i:i+20]
            logging.info(f"Processando lote {i//20 + 1} de {total_lotes}")
            dados_lote = obter_dados_fiis(lote)
            todos_dados.extend(dados_lote)
        
        # Filtrar FIIs com preço abaixo do máximo definido
        preco_maximo = float(os.getenv('MAX_PRICE', '25.0'))
        fiis_filtrados = [
            fii for fii in todos_dados 
            if fii.get('regularMarketPrice', float('inf')) <= preco_maximo
        ]
        
        # Salvar dados
        dados_final = {
            'atualizacao': datetime.now().isoformat(),
            'fiis': fiis_filtrados,
            'total': len(fiis_filtrados),
            'configuracoes': {
                'preco_maximo': preco_maximo,
                'rate_limit_delay': RATE_LIMIT_DELAY
            }
        }
        
        salvar_dados(dados_final, 'fiis_processados.json')
        logging.info(f"Processo finalizado com sucesso! Total de FIIs: {len(fiis_filtrados)}")
        
    except Exception as e:
        logging.error(f"Erro no processo principal: {e}")
        raise

if __name__ == "__main__":
    main()