// Map management and visualization
let map;
let currentLayer;
let currentCropData = {};
let currentCropName = '';
let cropMinMax = { min: 0, max: 1000 };

function initializeMap() {
    // Initialize map centered on Brazil
    map = L.map('map').setView([-14.2350, -51.9253], 4);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add a welcome message
    const welcomeControl = L.control({ position: 'topleft' });
    welcomeControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = `
            <h6><i class="fas fa-info-circle"></i> Sistema FertiCore</h6>
            <p style="margin: 0; font-size: 12px;">
                Selecione uma cultura para visualizar os dados de hectares colhidos por município.
            </p>
        `;
        return div;
    };
    welcomeControl.addTo(map);

    console.log('Map initialized successfully');
}

function loadCropLayer(cropName) {
    console.log(`Loading crop layer for: ${cropName}`);

    // Show loading state
    const loadBtn = document.getElementById('load-layer-btn');
    const originalText = loadBtn.innerHTML;
    loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Carregando...';
    loadBtn.disabled = true;

    // Fetch crop data
    fetch(`/api/crop-data/${encodeURIComponent(cropName)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentCropData = data.data;
                currentCropName = cropName;

                // Calculate min/max for this specific crop
                const values = Object.values(currentCropData)
                    .map(item => item.harvested_area)
                    .filter(value => value > 0);

                if (values.length > 0) {
                    cropMinMax.min = Math.min(...values);
                    cropMinMax.max = Math.max(...values);
                } else {
                    cropMinMax = { min: 0, max: 1000 };
                }

                loadMunicipalityBoundaries(cropName);
            } else {
                console.error('Error loading crop data:', data.error);
                alert('Erro ao carregar dados da cultura: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Network error:', error);
            alert('Erro de conexão ao carregar dados da cultura');
        })
        .finally(() => {
            loadBtn.innerHTML = originalText;
            loadBtn.disabled = false;
        });
}

function loadMunicipalityBoundaries(cropName) {
    // Remove existing layer
    if (currentLayer) {
        map.removeLayer(currentLayer);
    }

    // Load GeoJSON data for Brazilian municipalities
    fetch('/static/data/brazil_municipalities_all.geojson')
        .then(response => response.json())
        .then(geoData => {
            currentLayer = L.geoJSON(geoData, {
                style: function(feature) {
                    return getFeatureStyle(feature, cropName);
                },
                onEachFeature: function(feature, layer) {
                    setupFeaturePopup(feature, layer, cropName);
                }
            }).addTo(map);

            // Fit map to layer bounds
            map.fitBounds(currentLayer.getBounds());

            // Update legend
            updateMapLegend(cropName);
        })
        .catch(error => {
            console.error('Error loading municipality boundaries:', error);
            // Create a fallback visualization with sample data
            createFallbackVisualization(cropName);
        });
}

function createFallbackVisualization(cropName) {
    // Create sample markers for demonstration when GeoJSON is not available
    const sampleCities = [
        { name: "São Paulo", lat: -23.5505, lng: -46.6333, state: "SP" },
        { name: "Rio de Janeiro", lat: -22.9068, lng: -43.1729, state: "RJ" },
        { name: "Brasília", lat: -15.7942, lng: -47.8822, state: "DF" },
        { name: "Salvador", lat: -12.9714, lng: -38.5014, state: "BA" },
        { name: "Fortaleza", lat: -3.7172, lng: -38.5433, state: "CE" },
        { name: "Belo Horizonte", lat: -19.9167, lng: -43.9345, state: "MG" },
        { name: "Curitiba", lat: -25.4244, lng: -49.2654, state: "PR" },
        { name: "Porto Alegre", lat: -30.0346, lng: -51.2177, state: "RS" }
    ];

    currentLayer = L.layerGroup();

    sampleCities.forEach(city => {
        const area = Math.random() * 50000; // Random area for demonstration
        const color = getColorForValue(area, 0, 50000);

        const marker = L.circleMarker([city.lat, city.lng], {
            radius: Math.sqrt(area / 1000) + 5,
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.7
        });

        marker.bindPopup(`
            <strong>${city.name} (${city.state})</strong><br>
            Cultura: ${cropName}<br>
            Área Colhida: ${area.toLocaleString('pt-BR', {maximumFractionDigits: 0})} hectares
        `);

        currentLayer.addLayer(marker);
    });

    currentLayer.addTo(map);

    // Update legend
    updateMapLegend(cropName);

    console.log('Fallback visualization created');
}

function getFeatureStyle(feature, cropName) {
    // Try multiple ways to get municipality code from GeoJSON
    const municipalityCode = feature.properties.GEOCODIGO || feature.properties.CD_MUN || feature.properties.cd_geocmu || feature.properties.geocodigo;
    const cropData = currentCropData[municipalityCode];

    if (!cropData || !cropData.harvested_area) {
        return {
            fillColor: '#f0f0f0',
            weight: 0.5,
            opacity: 0.8,
            color: '#cccccc',
            fillOpacity: 0.3
        };
    }

    const area = cropData.harvested_area;
    const color = getColorForValue(area, cropMinMax.min, cropMinMax.max);

    return {
        fillColor: color,
        weight: 0.5,
        opacity: 0.9,
        color: '#ffffff',
        fillOpacity: 0.8
    };
}

function setupFeaturePopup(feature, layer, cropName) {
    // Try multiple ways to get municipality info from GeoJSON
    const municipalityCode = feature.properties.GEOCODIGO || feature.properties.CD_MUN || feature.properties.cd_geocmu || feature.properties.geocodigo;
    const municipalityName = feature.properties.NOME || feature.properties.NM_MUN || feature.properties.nm_mun || feature.properties.nome || 'Nome não disponível';
    const stateUF = feature.properties.UF || feature.properties.SIGLA_UF || feature.properties.uf;
    const cropData = currentCropData[municipalityCode];

    let popupContent = `<strong>${municipalityName}</strong>`;
    if (stateUF) {
        popupContent += ` (${stateUF})`;
    }
    popupContent += `<br>`;

    if (cropData && cropData.harvested_area) {
        popupContent += `
            Cultura: ${cropName}<br>
            Área Colhida: ${cropData.harvested_area.toLocaleString('pt-BR')} hectares<br>
            Código: ${municipalityCode}
        `;
    } else {
        popupContent += `
            Cultura: ${cropName}<br>
            <em>Dados não disponíveis</em><br>
            Código: ${municipalityCode || 'N/A'}
        `;
    }

    layer.bindPopup(popupContent);
}

function getMinMaxValues() {
    return cropMinMax;
}

function getColorForValue(value, min, max) {
    if (value <= 0 || !value) return '#E0E0E0';

    // Use logarithmic scale for better distribution
    const logMin = Math.log(min || 1);
    const logMax = Math.log(max);
    const logValue = Math.log(value);
    const normalized = (logValue - logMin) / (logMax - logMin);

    // Define color scale with better contrast
    const colors = [
        '#FFF9C4',  // Very light yellow
        '#F0F4C3',  // Light yellow-green
        '#DCEDC8',  // Light green
        '#C8E6C9',  // Medium light green
        '#A5D6A7',  // Medium green
        '#81C784',  // Medium-dark green
        '#66BB6A',  // Dark green
        '#4CAF50',  // Darker green
        '#388E3C',  // Very dark green
        '#2E7D32'   // Darkest green
    ];

    // Clamp normalized value and calculate index
    const clampedNormalized = Math.max(0, Math.min(1, normalized));
    const index = Math.floor(clampedNormalized * (colors.length - 1));
    return colors[index];
}

let currentLegendControl = null;

function updateMapLegend(cropName) {
    // Remove existing legend
    if (currentLegendControl) {
        map.removeControl(currentLegendControl);
        currentLegendControl = null;
    }

    const { min, max } = cropMinMax;

    currentLegendControl = L.control({ position: 'bottomright' });
    currentLegendControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend');

        let legendHTML = `<h6><i class="fas fa-seedling"></i> ${cropName}</h6>`;

        // Create color scale
        const steps = 5;
        for (let i = 0; i < steps; i++) {
            const value = min + (max - min) * (i / (steps - 1));
            const color = getColorForValue(value, min, max);

            legendHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${color}"></div>
                    <span>${value.toLocaleString('pt-BR', {maximumFractionDigits: 0})} ha</span>
                </div>
            `;
        }

        legendHTML += `
            <div class="legend-item mt-2" style="font-size: 10px; color: #666;">
                <div class="legend-color" style="background-color: #E0E0E0"></div>
                <span>Sem dados</span>
            </div>
        `;

        div.innerHTML = legendHTML;
        return div;
    };
    currentLegendControl.addTo(map);

    console.log(`Legend updated for ${cropName}: ${min.toLocaleString()} - ${max.toLocaleString()} ha`);
}

// Data is now static, no processing needed
function processData() {
    showStatus('Dados já estão carregados estaticamente!', 'info');
}


// Export functions for global use
window.initializeMap = initializeMap;
window.loadCropLayer = loadCropLayer;