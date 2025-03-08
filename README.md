# Dashboard de Análise de FIIs da B3

![Dashboard Preview](assets/img/dashboard-preview.png)

## Sobre o Projeto

Este dashboard foi desenvolvido para analisar Fundos de Investimento Imobiliário (FIIs) da B3, com foco em dividendos e rentabilidade. O sistema atualiza automaticamente os dados 3 vezes ao dia em dias úteis, utilizando APIs gratuitas.

### Funcionalidades

- **Tabela de FIIs**: Top 30 FIIs com preço abaixo de R$25,00, ordenados por critérios de rentabilidade
- **Filtros Dinâmicos**: Filtragem por setor, dividend yield mínimo e preço máximo
- **Análise Gráfica**: Distribuição por segmento e relação P/VP x DY
- **Recomendações por Perfil**: Sugestões para perfis conservador, moderado e arrojado
- **Atualização Automática**: Dados atualizados 3 vezes ao dia via GitHub Actions

### Métricas Analisadas

- **Dividend Yield (DY)**: Rendimento anual em relação ao preço atual
- **Último Dividendo**: Valor do último provento distribuído
- **P/VP**: Relação entre preço e valor patrimonial
- **Preço Justo**: Estimativa baseada em análise fundamentalista
- **Desconto/Prêmio**: Diferença percentual entre preço atual e preço justo

## Como Usar

1. Acesse o dashboard online: [https://seu-usuario.github.io/dashboard-fiis-b3/](https://seu-usuario.github.io/dashboard-fiis-b3/)
2. Utilize os filtros para personalizar sua análise
3. Consulte as recomendações por perfil de investidor
4. Verifique a data da última atualização no topo da página

## Instalação Local

Para executar o dashboard localmente:

