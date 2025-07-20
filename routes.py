import os
from flask import Flask, render_template, jsonify, request
from app import app
import json

# Load crop data
def load_crop_data():
    try:
        with open('data/processed_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo processed_data.json não encontrado")
        return {}
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return {}

CROP_DATA = load_crop_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/states')
def get_states():
    try:
        # Brazilian states
        states = [
            {'code': 'AC', 'name': 'Acre'},
            {'code': 'AL', 'name': 'Alagoas'},
            {'code': 'AP', 'name': 'Amapá'},
            {'code': 'AM', 'name': 'Amazonas'},
            {'code': 'BA', 'name': 'Bahia'},
            {'code': 'CE', 'name': 'Ceará'},
            {'code': 'DF', 'name': 'Distrito Federal'},
            {'code': 'ES', 'name': 'Espírito Santo'},
            {'code': 'GO', 'name': 'Goiás'},
            {'code': 'MA', 'name': 'Maranhão'},
            {'code': 'MT', 'name': 'Mato Grosso'},
            {'code': 'MS', 'name': 'Mato Grosso do Sul'},
            {'code': 'MG', 'name': 'Minas Gerais'},
            {'code': 'PA', 'name': 'Pará'},
            {'code': 'PB', 'name': 'Paraíba'},
            {'code': 'PR', 'name': 'Paraná'},
            {'code': 'PE', 'name': 'Pernambuco'},
            {'code': 'PI', 'name': 'Piauí'},
            {'code': 'RJ', 'name': 'Rio de Janeiro'},
            {'code': 'RN', 'name': 'Rio Grande do Norte'},
            {'code': 'RS', 'name': 'Rio Grande do Sul'},
            {'code': 'RO', 'name': 'Rondônia'},
            {'code': 'RR', 'name': 'Roraima'},
            {'code': 'SC', 'name': 'Santa Catarina'},
            {'code': 'SP', 'name': 'São Paulo'},
            {'code': 'SE', 'name': 'Sergipe'},
            {'code': 'TO', 'name': 'Tocantins'}
        ]

        return jsonify({
            'success': True,
            'states': states
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/statistics')
def get_statistics():
    try:
        # Count unique crops and municipalities
        crops = set()
        municipalities = set()

        for municipality_data in CROP_DATA.values():
            municipalities.add(municipality_data.get('municipality_name', ''))
            if 'crops' in municipality_data:
                crops.update(municipality_data['crops'].keys())

        return jsonify({
            'success': True,
            'total_crops': len(crops),
            'total_municipalities': len(municipalities)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/crops')
def get_crops():
    try:
        crops = set()
        for municipality_data in CROP_DATA.values():
            if 'crops' in municipality_data:
                crops.update(municipality_data['crops'].keys())

        sorted_crops = sorted(list(crops))
        return jsonify({
            'success': True,
            'crops': sorted_crops
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/crop-data/<crop_name>')
def get_crop_data(crop_name):
    try:
        crop_municipalities = {}

        for municipality_code, municipality_data in CROP_DATA.items():
            if 'crops' in municipality_data and crop_name in municipality_data['crops']:
                crop_municipalities[municipality_code] = {
                    'municipality_name': municipality_data.get('municipality_name', 'Desconhecido'),
                    'state_code': municipality_data.get('state_code', 'XX'),
                    'harvested_area': municipality_data['crops'][crop_name]
                }

        return jsonify({
            'success': True,
            'data': crop_municipalities
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/crop-chart-data/<crop_name>')
def get_crop_chart_data(crop_name):
    try:
        crop_municipalities = []

        for municipality_code, municipality_data in CROP_DATA.items():
            if 'crops' in municipality_data and crop_name in municipality_data['crops']:
                crop_municipalities.append({
                    'municipality_name': municipality_data.get('municipality_name', 'Desconhecido'),
                    'state_code': municipality_data.get('state_code', 'XX'),
                    'harvested_area': municipality_data['crops'][crop_name]
                })

        # Sort by harvested area and take top 20
        crop_municipalities.sort(key=lambda x: x['harvested_area'], reverse=True)
        top_20 = crop_municipalities[:20]

        chart_data = {
            'labels': [f"{muni['municipality_name']} ({muni['state_code']})" for muni in top_20],
            'values': [muni['harvested_area'] for muni in top_20]
        }

        return jsonify({
            'success': True,
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)