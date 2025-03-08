import requests
import json
import os
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Configuração de logging
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
    headers = {'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def obter_lista_fiis():
    """Obtém lista de todos os FIIs disponíveis"""
    try:
        url = "https://brapi.dev/api/quote/list?type=fii"
        dados = obter_dados_api(url)
        
        if not dados or 'stocks' not in dados:
            raise ValueError("Dados inválidos retornados pela API")
            
        # Filtrar apenas FIIs (terminam com '11')
        return [item for item in dados['stocks'] if item['stock'].endswith('11')]
    except Exception as e:
        logging.error(f"Erro ao obter lista de FIIs: {e}")
        return []

def obter_dados_fiis(tickers):
    """Obtém dados detalhados dos FIIs especificados"""
    try:
        dados_fiis = []
        for ticker in tickers:
            logging.info(f"Obtendo dados do FII {ticker}")
            url = f"https://brapi.dev/api/quote/{ticker}?fundamental=true"
            dados = obter_dados_api(url)
            
            if dados and 'results' in dados and dados['results']:
                fii = dados['results'][0]
                # Validar e processar dados importantes
                if validar_dados_fii(fii):
                    dados_fiis.append(fii)
                else:
                    logging.warning(f"Dados incompletos para {ticker}")
            
            # Pequena pausa para não sobrecarregar a API
            time.sleep(0.5)
            
        return dados_fiis
    except Exception as e:
        logging.error(f"Erro ao obter dados dos FIIs: {e}")
        return []

def validar_dados_fii(fii):
    """Valida se os dados essenciais do FII estão presentes"""
    campos_obrigatorios = [
        'symbol',
        'regularMarketPrice',
        'dividendYield',
        'longName'
    ]
    return all(campo in fii and fii[campo] is not None for campo in campos_obrigatorios)

def salvar_dados(dados, nome_arquivo='fiis.json'):
    """Salva os dados em formato JSON"""
    try:
        # Salvar arquivo atual
        caminho_arquivo = os.path.join(DATA_DIR, nome_arquivo)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        # Salvar cópia no histórico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        caminho_historico = os.path.join(HISTORICO_DIR, f'fiis_{timestamp}.json')
        with open(caminho_historico, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Dados salvos em {caminho_arquivo} e {caminho_historico}")
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")
        raise

def main():
    try:
        # Obter todos os FIIs disponíveis
        logging.info("Iniciando coleta de dados...")
        todos_fiis = obter_lista_fiis()
        
        if not todos_fiis:
            raise ValueError("Nenhum FII encontrado")
        
        # Extrair apenas os tickers
        tickers = [fii['stock'] for fii in todos_fiis]
        logging.info(f"Encontrados {len(tickers)} FIIs")
        
        # Obter dados detalhados (em lotes de 20)
        todos_dados = []
        for i in range(0, len(tickers), 20):
            lote = tickers[i:i+20]
            logging.info(f"Processando lote {i//20 + 1} de {len(tickers)//20 + 1}")
            dados_lote = obter_dados_fiis(lote)
            todos_dados.extend(dados_lote)
        
        # Filtrar FIIs com preço abaixo de R$ 25,00
        preco_maximo = float(os.getenv('MAX_PRICE', '25.0'))
        fiis_filtrados = [
            fii for fii in todos_dados 
            if fii.get('regularMarketPrice', 0) < preco_maximo
        ]
        
        # Salvar dados
        dados_final = {
            'atualizacao': datetime.now().isoformat(),
            'fiis': fiis_filtrados,
            'total': len(fiis_filtrados)
        }
        salvar_dados(dados_final)
        logging.info("Processo finalizado com sucesso!")
        
    except Exception as e:
        logging.error(f"Erro no processo principal: {e}")
        raise

if __name__ == "__main__":
    main()
