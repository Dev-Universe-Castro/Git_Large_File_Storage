import json
import os
import logging
from flask import render_template, jsonify, request
from app import app, db
from models import CropData, ProcessingLog
from data_processor import process_ibge_data, get_available_crops, get_crop_data_for_map

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get available crops for the selector
        crops = get_available_crops()
        total_municipalities = db.session.query(CropData.municipality_code).distinct().count()
        total_crops = len(crops)
        
        return render_template('index.html', 
                             crops=crops, 
                             total_municipalities=total_municipalities,
                             total_crops=total_crops)
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

@app.route('/api/process-data')
def api_process_data():
    """API endpoint to process IBGE data"""
    try:
        # Check if we have the Excel file
        excel_path = 'attached_assets/tabela5457_1752835669304_1752899290708.xlsx'
        if not os.path.exists(excel_path):
            return jsonify({"success": False, "error": "IBGE data file not found"})
        
        result = process_ibge_data(excel_path)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/statistics')
def api_get_statistics():
    """API endpoint to get general statistics"""
    try:
        stats = {
            "total_municipalities": db.session.query(CropData.municipality_code).distinct().count(),
            "total_crops": db.session.query(CropData.crop_name).distinct().count(),
            "total_records": CropData.query.count(),
            "last_update": db.session.query(ProcessingLog.processed_at).order_by(ProcessingLog.processed_at.desc()).first()
        }
        
        if stats["last_update"]:
            stats["last_update"] = stats["last_update"][0].isoformat()
        
        return jsonify({"success": True, "statistics": stats})
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/crop-chart-data/<crop_name>')
def api_get_crop_chart_data(crop_name):
    """API endpoint to get crop data for chart visualization"""
    try:
        # Get top 20 municipalities by harvested area for the crop
        crop_data = db.session.query(
            CropData.municipality_name,
            CropData.state_code,
            CropData.harvested_area
        ).filter(
            CropData.crop_name == crop_name
        ).order_by(
            CropData.harvested_area.desc()
        ).limit(20).all()
        
        chart_data = {
            "labels": [f"{row[0]} ({row[1]})" for row in crop_data],
            "data": [float(row[2]) for row in crop_data],
            "crop_name": crop_name
        }
        
        return jsonify({"success": True, "chart_data": chart_data})
    except Exception as e:
        logger.error(f"Error getting chart data for {crop_name}: {e}")
        return jsonify({"success": False, "error": str(e)})
