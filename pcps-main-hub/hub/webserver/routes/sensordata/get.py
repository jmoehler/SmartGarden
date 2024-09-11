from flask import Blueprint, jsonify, request
from flask_login import login_required
import logging

from database.database_setup import db_handler

sensordata_get_bp = Blueprint('sensordata_get', __name__, url_prefix='')

logger = logging.getLogger('BACKEND(history_get)')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(sh)

#################################################################
#
#   SENSOR LATEST DATA ROUTES
#
#################################################################
@sensordata_get_bp.route('get_data_for_day', methods=['GET'])
@login_required
def get_data_for_day():
    try:
        date = request.args.get('date')
    except:
        return jsonify({"Bad Request"}), 400
    try:
        logger.info(date)
        data_for_day = {}
        with db_handler() as db:
            data_for_day['ph'] = db.get_sensor_data_day('ph', date)
            data_for_day['ec'] = db.get_sensor_data_day('ec', date)
            data_for_day['humidity'] = db.get_sensor_data_day('humidity', date)
            data_for_day['waterlevel'] = db.get_sensor_data_day('waterlevel', date)
            data_for_day['temperature'] = db.get_sensor_data_day('temperature', date)
            data_for_day['light'] = db.get_sensor_data_day('light', date)

            return jsonify({"day_data": data_for_day})
    except:
        logger.error("Error: something went wrong")
        return jsonify({'Error: something went wrong'}), 500

@sensordata_get_bp.route('/get_ph', methods=['GET'])
@login_required
def get_ph():
    with db_handler() as db:
        data = db.get_sensor_data_most_recent("ph")
        return jsonify({
            'ph': {"entries": data}
        })


@sensordata_get_bp.route('/get_ec', methods=['GET'])
@login_required
def get_ec():
    with db_handler() as db:
        data = db.get_sensor_data_most_recent("ec")
        return jsonify({
            'ec': {"entries": data}
        })

@sensordata_get_bp.route('/get_waterlevel', methods=['GET'])
@login_required
def get_waterlevel():
    with db_handler() as db:
        data = db.get_sensor_data_most_recent("waterlevel")
        return jsonify({
            'waterlevel': {"entries": data}
        })

@sensordata_get_bp.route('/get_temperature', methods=['GET'])
@login_required
def get_temperature():
    with db_handler() as db:
        data = db.get_sensor_data_most_recent("temperature")
        return jsonify({
            'temperature': {"entries": data}
        })

@sensordata_get_bp.route('/get_humidity', methods=['GET'])
@login_required
def get_humidity():
    with db_handler() as db:
        data = db.get_sensor_data_most_recent("humidity")
        return jsonify({
            'humidity': {"entries": data}
        })

@sensordata_get_bp.route('/get_light', methods=['GET'])
@login_required
def get_light():
    with db_handler() as db:
        data = db.get_sensor_data_most_recent("light")
        return jsonify({
            'light': {"entries": data}
        })