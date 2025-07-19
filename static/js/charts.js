// Chart management and visualization
let cropChart = null;

function loadCropChart(cropName) {
    console.log(`Loading chart for crop: ${cropName}`);
    
    // Show chart container, hide placeholder
    document.getElementById('crop-chart').style.display = 'block';
    document.getElementById('chart-placeholder').style.display = 'none';
    
    // Fetch chart data
    fetch(`/api/crop-chart-data/${encodeURIComponent(cropName)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                createCropChart(data.chart_data);
            } else {
                console.error('Error loading chart data:', data.error);
                showChartError('Erro ao carregar dados do gráfico');
            }
        })
        .catch(error => {
            console.error('Network error loading chart:', error);
            showChartError('Erro de conexão ao carregar gráfico');
        });
}

function createCropChart(chartData) {
    const ctx = document.getElementById('crop-chart').getContext('2d');
    
    // Destroy existing chart
    if (cropChart) {
        cropChart.destroy();
    }
    
    const config = {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Hectares Colhidos',
                data: chartData.data,
                backgroundColor: generateGradientColors(chartData.data.length),
                borderColor: '#4CAF50',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Top 20 Municípios - ${chartData.crop_name}`,
                    font: {
                        size: 14,
                        weight: 'bold'
                    },
                    color: '#2E7D32'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.x.toLocaleString('pt-BR')} hectares`;
                        }
                    }
                }
            },
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('pt-BR');
                        }
                    },
                    title: {
                        display: true,
                        text: 'Hectares Colhidos'
                    }
                },
                y: {
                    ticks: {
                        maxTicksLimit: 20,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    };
    
    // Create chart
    cropChart = new Chart(ctx, config);
    
    console.log('Chart created successfully');
}

function generateGradientColors(count) {
    const colors = [];
    const baseColors = [
        '#E8F5E8', '#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A',
        '#4CAF50', '#43A047', '#388E3C', '#2E7D32', '#1B5E20'
    ];
    
    for (let i = 0; i < count; i++) {
        const intensity = Math.floor((i / count) * baseColors.length);
        colors.push(baseColors[Math.min(intensity, baseColors.length - 1)]);
    }
    
    return colors;
}

function showChartError(message) {
    document.getElementById('crop-chart').style.display = 'none';
    
    const placeholder = document.getElementById('chart-placeholder');
    placeholder.innerHTML = `
        <i class="fas fa-exclamation-triangle fa-3x mb-3 text-warning"></i>
        <p class="text-muted">${message}</p>
    `;
    placeholder.style.display = 'block';
}

function clearChart() {
    if (cropChart) {
        cropChart.destroy();
        cropChart = null;
    }
    
    document.getElementById('crop-chart').style.display = 'none';
    
    const placeholder = document.getElementById('chart-placeholder');
    placeholder.innerHTML = `
        <i class="fas fa-chart-bar fa-3x mb-3 opacity-25"></i>
        <p>Selecione uma cultura para visualizar o gráfico</p>
    `;
    placeholder.style.display = 'block';
}

// Initialize chart management
document.addEventListener('DOMContentLoaded', function() {
    // Ensure Chart.js uses the correct bar chart type
    if (typeof Chart !== 'undefined') {
        Chart.defaults.set('plugins.legend', {
            display: false
        });
    }
});

// Export functions for global use
window.loadCropChart = loadCropChart;
window.clearChart = clearChart;
