document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados dos FIIs
    fetch('data/fiis_processados.json')
        .then(response => response.json())
        .then(data => {
            const fiis = data.fiis;
            
            // Inicializar filtros
            inicializarFiltros(fiis);
            
            // Inicializar gráficos
            inicializarGraficos(fiis);
            
            // Gerar recomendações por perfil
            gerarRecomendacoes(fiis);
        })
        .catch(error => console.error('Erro ao carregar dados:', error));
    
    // Configurar evento de filtro
    document.getElementById('aplicar-filtros').addEventListener('click', aplicarFiltros);
});

function inicializarFiltros(fiis) {
    // Preencher opções de setores
    const setores = [...new Set(fiis.map(fii => fii.sector).filter(Boolean))];
    const seletorSetor = document.getElementById('filtro-setor');
    
    // Limpar opções existentes, mantendo a opção "Todos"
    while (seletorSetor.options.length > 1) {
        seletorSetor.remove(1);
    }
    
    // Adicionar setores encontrados
    setores.forEach(setor => {
        const option = document.createElement('option');
        option.value = setor;
        option.textContent = setor;
        seletorSetor.appendChild(option);
    });
}

function aplicarFiltros() {
    const setorSelecionado = document.getElementById('filtro-setor').value;
    const dyMinimo = parseFloat(document.getElementById('filtro-dy').value);
    const precoMaximo = parseFloat(document.getElementById('filtro-preco').value);
    
    // Obter todas as linhas da tabela
    const linhas = document.querySelectorAll('#tabela-fiis tbody tr');
    
    linhas.forEach(linha => {
        const setor = linha.cells[1].textContent;
        const preco = parseFloat(linha.cells[2].textContent.replace('R$', '').replace(',', '.'));
        const dy = parseFloat(linha.cells[3].textContent.replace('%', '').replace(',', '.'));
        
        // Aplicar filtros
        const mostrarPorSetor = setorSelecionado === 'todos' || setor === setorSelecionado;
        const mostrarPorDY = dy >= dyMinimo;
        const mostrarPorPreco = preco <= precoMaximo;
        
        // Mostrar ou esconder linha
        if (mostrarPorSetor && mostrarPorDY && mostrarPorPreco) {
            linha.style.display = '';
        } else {
            linha.style.display = 'none';
        }
    });
}

function inicializarGraficos(fiis) {
    // Gráfico de distribuição por segmento
    const segmentos = {};
    fiis.forEach(fii => {
        const setor = fii.sector || 'Não classificado';
        segmentos[setor] = (segmentos[setor] || 0) + 1;
    });
    
    const ctxSegmentos = document.getElementById('grafico-segmentos').getContext('2d');
    new Chart(ctxSegmentos, {
        type: 'pie',
        data: {
            labels: Object.keys(segmentos),
            datasets: [{
                data: Object.values(segmentos),
                backgroundColor: [
                    '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
                    '#9b59b6', '#1abc9c', '#34495e', '#d35400'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
    
    // Gráfico de relação P/VP x DY
    const dadosGrafico = fiis.map(fii => ({
        x: fii.priceToBook || 0,
        y: (fii.dividendYield || 0) * 100,
        r: 8,
        label: fii.symbol
    }));
    
    const ctxPvpDy = document.getElementById('grafico-pvp-dy').getContext('2d');
    new Chart(ctxPvpDy, {
        type: 'bubble',
        data: {
            datasets: [{
                data: dadosGrafico,
                backgroundColor: 'rgba(52, 152, 219, 0.6)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'P/VP'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'DY Anual (%)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return `${point.label}: P/VP ${point.x.toFixed(2)}, DY ${point.y.toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}

function gerarRecomendacoes(fiis) {
    // Classificar FIIs por tipo
    const recebiveis = fiis.filter(fii => fii.sector === 'Recebíveis');
    const logisticos = fiis.filter(fii => fii.sector === 'Logístico');
    const shoppings = fiis.filter(fii => fii.sector === 'Shopping');
    const escritorios = fiis.filter(fii => fii.sector === 'Escritórios');
    const fundosDeFundos = fiis.filter(fii => fii.sector === 'Fundo de Fundos');
    
    // Ordenar por critérios específicos para cada perfil
    const conservadores = [...recebiveis].sort((a, b) => (b.dividendYield || 0) - (a.dividendYield || 0)).slice(0, 3);
    const moderados = [
        ...recebiveis.slice(0, 2),
        ...logisticos.slice(0, 2),
        ...shoppings.slice(0, 1)
    ];
    const arrojados = [
        ...logisticos.slice(0, 2),
        ...shoppings.slice(0, 2),
        ...escritorios.filter(fii => (fii.desconto || 0) > 10).slice(0, 1)
    ];
    
    // Exibir recomendações
    exibirRecomendacoes('recomendacoes-conservador', conservadores);
    exibirRecomendacoes('recomendacoes-moderado', moderados);
    exibirRecomendacoes('recomendacoes-arrojado', arrojados);
}

function exibirRecomendacoes(elementId, fiis) {
    const elemento = document.getElementById(elementId);
    elemento.innerHTML = '';
    
    fiis.forEach(fii => {
        const li = document.createElement('li');
        const dy = ((fii.dividendYield || 0) * 100).toFixed(2);
        li.innerHTML = `<strong>${fii.symbol}</strong> - DY: ${dy}% - P/VP: ${fii.priceToBook?.toFixed(2) || 'N/A'}`;
        elemento.appendChild(li);
    });
}
