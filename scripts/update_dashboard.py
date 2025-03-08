import os
import json
from datetime import datetime
import subprocess

def atualizar_dados():
    """Executa os scripts para atualizar os dados"""
    try:
        # Executar script para obter dados
        print("Obtendo dados da API...")
        subprocess.run(["python", "scripts/fetch_data.py"], check=True)
        
        # Executar script para processar dados
        print("Processando dados...")
        subprocess.run(["python", "scripts/process_data.py"], check=True)
        
        print("Dados atualizados com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao atualizar dados: {e}")
        return False

def gerar_html():
    """Gera o HTML do dashboard com os dados atualizados"""
    try:
        # Carregar dados processados
        with open('data/fiis_processados.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Extrair informações
        atualizacao = datetime.fromisoformat(dados['atualizacao']).strftime('%d/%m/%Y %H:%M')
        fiis = dados['fiis']
        
        # Gerar HTML da tabela
        linhas_tabela = ""
        for fii in fiis:
            ticker = fii.get('symbol', '')
            nome = fii.get('longName', ticker)
            preco = fii.get('regularMarketPrice', 0)
            dy_anual = fii.get('dividendYield', 0) * 100
            ultimo_dividendo = fii.get('lastDividend', {}).get('value', 0)
            dy_mensal = (ultimo_dividendo / preco) * 100 if preco > 0 else 0
            p_vp = fii.get('priceToBook', 0)
            preco_justo = fii.get('precoJusto', 0)
            desconto = fii.get('desconto', 0)
            setor = fii.get('sector', 'N/A')
            
            # Formatar valores
            preco_str = f"R$ {preco:.2f}".replace('.', ',')
            dy_anual_str = f"{dy_anual:.2f}%".replace('.', ',')
            ultimo_dividendo_str = f"R$ {ultimo_dividendo:.4f}".replace('.', ',')
            dy_mensal_str = f"{dy_mensal:.2f}%".replace('.', ',')
            p_vp_str = f"{p_vp:.2f}".replace('.', ',')
            preco_justo_str = f"R$ {preco_justo:.2f}".replace('.', ',')
            desconto_str = f"{desconto:.2f}%".replace('.', ',')
            
            # Determinar classe CSS para desconto
            desconto_class = "positivo" if desconto > 0 else "negativo"
            
            # Adicionar linha à tabela
            linhas_tabela += f"""
            <tr>
                <td><a href="https://www.fundamentus.com.br/detalhes.php?papel={ticker}" target="_blank">{ticker}</a></td>
                <td>{setor}</td>
                <td>{preco_str}</td>
                <td>{dy_anual_str}</td>
                <td>{ultimo_dividendo_str} ({dy_mensal_str})</td>
                <td>{p_vp_str}</td>
                <td>{preco_justo_str}</td>
                <td class="{desconto_class}">{desconto_str}</td>
            </tr>
            """
        
        # Ler template HTML
        with open('assets/template.html', 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Substituir placeholders
        html = template.replace('{{ATUALIZACAO}}', atualizacao)
        html = html.replace('{{LINHAS_TABELA}}', linhas_tabela)
        
        # Salvar HTML gerado
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("HTML do dashboard gerado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao gerar HTML: {e}")
        return False

def main():
    # Atualizar dados
    if atualizar_dados():
        # Gerar HTML
        gerar_html()

if __name__ == "__main__":
    main()
