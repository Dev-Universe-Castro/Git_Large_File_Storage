
import json
import os
from flask import jsonify
from app import app

# Load static crop data
def load_static_crop_data():
    """Load crop data from static JSON file"""
    try:
        with open('data/crop_data_static.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: crop_data_static.json not found, using fallback data")
        return {}

STATIC_CROP_DATA = load_static_crop_data()

@app.route('/')
def index():
    return app.send_static_file('index.html') if os.path.exists('static/index.html') else \
           render_template('index.html')

@app.route('/api/crops')
def get_available_crops():
    """Get list of all available crops"""
    try:
        crops = list(STATIC_CROP_DATA.keys())
        return jsonify({
            'success': True,
            'crops': sorted(crops)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/crop-data/<crop_name>')
def get_crop_data(crop_name):
    """Get crop data for a specific crop"""
    try:
        if crop_name not in STATIC_CROP_DATA:
            return jsonify({
                'success': False,
                'error': f'Crop "{crop_name}" not found'
            }), 404
        
        crop_data = STATIC_CROP_DATA[crop_name]
        
        return jsonify({
            'success': True,
            'data': crop_data,
            'crop_name': crop_name,
            'total_municipalities': len(crop_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics')
def get_statistics():
    """Get general statistics"""
    try:
        total_crops = len(STATIC_CROP_DATA)
        total_municipalities = len(set(
            municipality_code 
            for crop_data in STATIC_CROP_DATA.values() 
            for municipality_code in crop_data.keys()
        ))
        total_records = sum(len(crop_data) for crop_data in STATIC_CROP_DATA.values())
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_crops': total_crops,
                'total_municipalities': total_municipalities,
                'total_records': total_records,
                'last_update': '2023-12-31T00:00:00'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/crop-chart/<crop_name>')
def get_crop_chart_data(crop_name):
    """Get crop data formatted for chart visualization"""
    try:
        if crop_name not in STATIC_CROP_DATA:
            return jsonify({
                'success': False,
                'error': f'Crop "{crop_name}" not found'
            }), 404
        
        crop_data = STATIC_CROP_DATA[crop_name]
        
        # Convert to list and sort by harvested area
        chart_data = []
        for municipality_code, data in crop_data.items():
            chart_data.append({
                'municipality_name': data['municipality_name'],
                'state_code': data['state_code'],
                'harvested_area': data['harvested_area'],
                'municipality_code': municipality_code
            })
        
        # Sort by harvested area descending and take top 20
        chart_data.sort(key=lambda x: x['harvested_area'], reverse=True)
        chart_data = chart_data[:20]
        
        return jsonify({
            'success': True,
            'data': {
                'labels': [f"{item['municipality_name']} ({item['state_code']})" for item in chart_data],
                'data': [item['harvested_area'] for item in chart_data],
                'crop_name': crop_name
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
