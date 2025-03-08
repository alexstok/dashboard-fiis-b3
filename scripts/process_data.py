import json
import os
import math
from datetime import datetime

# Diretório para armazenar os dados
DATA_DIR = 'data'

def carregar_dados(nome_arquivo='fiis.json'):
    """Carrega os dados do arquivo JSON"""
    try:
        caminho_arquivo = os.path.join(DATA_DIR, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return {'atualizacao': '', 'fiis': []}

def calcular_metricas_adicionais(fiis):
    """Calcula métricas adicionais para cada FII"""
    for fii in fiis:
        # Calcular preço justo baseado no P/VP médio histórico (simplificado)
        p_vp = fii.get('priceToBook', 1.0)
        valor_patrimonial = fii.get('bookValue', 0)
        
        # Se P/VP estiver abaixo de 0.8, consideramos descontado
        p_vp_medio_historico = 1.0  # Valor de referência
        preco_justo = valor_patrimonial * p_vp_medio_historico
        
        # Adicionar métricas calculadas
        fii['precoJusto'] = round(preco_justo, 2)
        fii['desconto'] = round((1 - (fii.get('regularMarketPrice', 0) / preco_justo)) * 100, 2) if preco_justo > 0 else 0
        
        # Calcular pontuação (score) para ranking
        dy = fii.get('dividendYield', 0) * 100  # Convertendo para percentual
        desconto = fii['desconto']
        liquidez = min(fii.get('avgDailyVolume10Day', 0) / 1000000, 10)  # Normalizado para 0-10
        
        # Fórmula de pontuação: 50% DY + 30% desconto + 20% liquidez
        fii['score'] = round(0.5 * dy + 0.3 * desconto + 0.2 * liquidez, 2)
    
    return fiis

def ordenar_fiis(fiis, criterio='score', limite=30):
    """Ordena os FIIs pelo critério especificado e limita a quantidade"""
    try:
        fiis_ordenados = sorted(fiis, key=lambda x: x.get(criterio, 0), reverse=True)
        return fiis_ordenados[:limite]
    except Exception as e:
        print(f"Erro ao ordenar FIIs: {e}")
        return fiis[:limite]

def salvar_dados_processados(dados, nome_arquivo='fiis_processados.json'):
    """Salva os dados processados em um arquivo JSON"""
    try:
        caminho_arquivo = os.path.join(DATA_DIR, nome_arquivo)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"Dados processados salvos em {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar dados processados: {e}")

def main():
    # Carregar dados
    dados = carregar_dados()
    
    # Calcular métricas adicionais
    fiis_com_metricas = calcular_metricas_adicionais(dados['fiis'])
    
    # Ordenar por pontuação e limitar aos 30 melhores
    melhores_fiis = ordenar_fiis(fiis_com_metricas, 'score', 30)
    
    # Salvar dados processados
    dados_processados = {
        'atualizacao': datetime.now().isoformat(),
        'fiis': melhores_fiis
    }
    salvar_dados_processados(dados_processados)

def validar_fii(fii):
    """Valida dados essenciais do FII"""
    campos_obrigatorios = {
        'symbol': str,
        'regularMarketPrice': (int, float),
        'dividendYield': (int, float),
        'sector': str
    }
    
    for campo, tipo in campos_obrigatorios.items():
        if campo not in fii or not isinstance(fii[campo], tipo):
            return False
    return True

def processar_dados(fiis):
    """Processa apenas FIIs com dados válidos"""
    return [fii for fii in fiis if validar_fii(fii)]

if __name__ == "__main__":
    main()
