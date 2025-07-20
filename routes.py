import json
import os
import logging
from flask import render_template, jsonify, request
from app import app

# Import static data
import sys
sys.path.append('static/data')
from crop_data import get_available_crops, get_crop_data_for_map, get_crop_chart_data, get_statistics

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get available crops and statistics
        crops = get_available_crops()
        stats = get_statistics()

        return render_template('index.html', 
                             crops=crops, 
                             total_municipalities=stats["total_municipalities"],
                             total_crops=stats["total_crops"])
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        return render_template('index.html', crops=[], total_municipalities=0, total_crops=0)

@app.route('/api/crops')
def api_get_crops():
    """API endpoint to get available crops"""
    try:
        crops = get_available_crops()
        return jsonify({"success": True, "crops": crops})
    except Exception as e:
        logger.error(f"Error getting crops: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/crop-data/<crop_name>')
def api_get_crop_data(crop_name):
    """API endpoint to get crop data for map visualization"""
    try:
        data = get_crop_data_for_map(crop_name)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error getting crop data for {crop_name}: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/statistics')
def api_get_statistics():
    """API endpoint to get general statistics"""
    try:
        stats = get_statistics()
        return jsonify({"success": True, "statistics": stats})
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/crop-chart-data/<crop_name>')
def api_get_crop_chart_data(crop_name):
    """API endpoint to get crop data for chart visualization"""
    try:
        chart_data = get_crop_chart_data(crop_name)
        return jsonify({"success": True, "chart_data": chart_data})
    except Exception as e:
        logger.error(f"Error getting chart data for {crop_name}: {e}")
        return jsonify({"success": False, "error": str(e)})