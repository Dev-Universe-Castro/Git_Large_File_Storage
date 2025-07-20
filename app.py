import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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
        # Count unique crops
        crops = set()
        municipalities = set()

        # Assuming CROP_DATA is available
        # Example:
        # from your_data_source import CROP_DATA
        CROP_DATA = {}  # Replace with your actual data source

        for muni_data in CROP_DATA.values():
            municipalities.add(muni_data['municipality_name'])
            if 'crops' in muni_data:
                crops.update(muni_data['crops'].keys())

        return jsonify({
            'success': True,
            'total_crops': len(crops),
            'total_municipalities': len(municipalities)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Import routes
import routes