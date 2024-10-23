from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging

from database.database_setup import DatabaseHandler, db_handler
from api.filterSpikes import spike_detected

# configure logging
sensors_logger = logging.getLogger('API(SENSORS)')
sensors_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
sensors_logger.addHandler(sh)

sensors_bp = Blueprint('sensors', __name__, url_prefix='/api/sensors')
CORS(sensors_bp, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@sensors_bp.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store')
    return response

"""
Endpoint for retrieving data from a specific sensor.

Parameters:
- 'sensor_type': Type of the sensor ('ph', 'ec', 'waterlevel',
                 'temperature', 'humidity', 'light') in the body of the request.
- 'Authorization': API key in the request header for device authorization.

Returns:
- JSON response with sensor data if the device is authorized and of type 'client-device'.
- Error response with appropriate status codes for unauthorized, disallowed, or non-existent sensor requests.
""" 
@sensors_bp.route('<sensor_type>', methods=['GET'])
def get_sensor_data(sensor_type):
    with db_handler() as db:
        api_key = request.headers.get("Authorization")
        
        if api_key == None:
            sensors_logger.error("Recieved request with no Authorization header")
            return jsonify({"error": "no Authorization header"}), 400
        
        authorized, _, device_type = None, None, None
        
        try:
            authorized, _, device_type = db.check_authorization(api_key)
        except Exception as e:
            sensors_logger.error(f"Something went wrong while checking authorization <{e}>")
            return jsonify({"error": "internal server error"}), 500
        
        if not authorized:
            sensors_logger.error("Recieved unauthorized request")
            return jsonify({"error": "unauthorized"}), 401
        
        if device_type != "client-device":
            sensors_logger.error("Recieved request from non-client device")
            return jsonify({"error": "method not allowed"}), 405
        
        if sensor_type not in ["ph", "ec", "waterlevel", "temperature", "humidity", "light"]:
            sensors_logger.error("Recieved request with invalid sensor type")
            return jsonify({"error": "sensor not found"}), 404

        start = request.args.get("start")
        end = request.args.get("end")
        max_entries = request.args.get("max_entries")
            
        try:
            data = db.get_sensor_data(sensor_type, start, end, max_entries)
            return jsonify({"entries": data}), 200
        except:
            sensors_logger.error("Something went wrong while getting sensor data")
            return jsonify({"error": "invalid data or parameters"}), 400


"""
Endpoint for pushing sensor data to the server.

Parameters:
- 'sensor_type': Type of the sensor ('ph', 'ec', 'waterlevel',
                 'temperature', 'humidity', 'light') in the body of the request.
- 'Authorization': API key in the request header for device authorization.

Returns:
- JSON response confirming successful data push if the device is authorized and of type 'sensor-device'.
- Error response with appropriate status codes for unauthorized, disallowed, or non-existent sensor requests.
"""

@sensors_bp.route('<sensor_type>', methods=['POST'])
def push_sensor_data(sensor_type):
    with db_handler() as db:        
        api_key = request.headers.get("Authorization")
        
        if api_key == None:
            sensors_logger.error("Recieved request with no Authorization header")
            return jsonify({"error": "no Authorization header"}), 400
        
        authorized, device_id, device_type = None, None, None
        
        try:
            authorized, device_id, device_type = db.check_authorization(api_key)
        except Exception as e:
            sensors_logger.error(f"Something went wrong while checking authorization <{e}>")
            return jsonify({"error": "internal server error"}), 500
        
        if not authorized:
            return jsonify({"error": "unauthorized"}), 401
        
        if device_type != "sensor-device":
            return jsonify({"error": "method not allowed"}), 405

        if sensor_type not in ["ph", "ec", "waterlevel", "temperature", "humidity", "light"]:
            return jsonify({"error": "sensor not found"}), 404
        
        data = None
        try:
            data = request.get_json()
        except:
            sensors_logger.error("Recieved request with no json payload")
            return jsonify({"error": "wrong payload type"}), 415
        
    
        data = dict(data)

        try:
            if spike_detected(sensor_type, data):
                sensors_logger.info("Spike detected for sensor type <{sensor_type}>. Data not pushed.")
                return jsonify({"error": "spike detected in data"}), 400
        except:
            sensors_logger.error("Something went wrong while checking for spikes")
            return jsonify({"error": "internal server error"}), 500

        try:
            if sensor_type == "ec":
                data["ec"] = float(data["ec"]) / 700.0
            db.add_sensor_data(device_id, sensor_type, data)
            return {"message": "data successfully pushed"}, 200
        except Exception as e:
            sensors_logger.error(f"Something went wrong while adding sensor data <{e}>")
            return jsonify({"error": "invalid data"}), 400
