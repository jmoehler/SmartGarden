from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from database.database_setup import db_handler

history_get_bp = Blueprint('history_get', __name__, url_prefix='')

#################################################################
#
#   SENSOR HISTORICAL DATA ROUTES
#
#################################################################
    
@history_get_bp.route('/get_hist_data', methods=['GET'])
@login_required
def get_hist_data():   
    return jsonify({
        'ph': extract_values('ph', 'ph_value'),
        'ec': extract_values('ec', 'ec_value'),
        'waterlevel': extract_values('waterlevel', 'waterlevel_value'),
        'temperature': extract_values('temperature', 'temperature_value'),
        'humidity': extract_values('humidity', 'humidity_value'),
        'light': extract_values('light', 'visible_value')
    })

@staticmethod
def extract_values(sensor_data, value_key):
        with db_handler() as db:
            data = db.get_sensor_data(sensor_data, None, None, 10)
            return [measurement[value_key] for measurement in data] 
        
