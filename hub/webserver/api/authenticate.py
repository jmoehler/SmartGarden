from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import secrets
import re
import logging

from database.database_setup import db_handler

# configure logging
auth_logger = logging.getLogger('API(AUTH)')
auth_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
auth_logger.addHandler(sh)


authenticate_bp = Blueprint('authenticate', __name__, url_prefix='/api/authenticate')
CORS(authenticate_bp, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@authenticate_bp.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store')
    return response

"""
Endpoint for registering devices with the authentication service.

Parameters:
- 'device_type': Type of the device ('sensor-device', 'actuator-device', 'webserver')
                 in the body of the request.
- 'device_id': Unique identifier for the device (MAC address).

Returns:
- JSON response containing the API key upon successful registration.
- Error response if the provided data is invalid or incomplete.
""" 
@authenticate_bp.route('', methods=['POST'])
def register_device():
    #################################
    # PARSE AND VALIDATE REQUEST
    
    # check if json payload is provided
    data = None
    try:
        data = request.get_json()
    except:
        auth_logger.error("Recieved request with no json payload")
        return jsonify({"error": "wrong payload type"}), 415
    
    # extract data from json payload
    device_id = data.get("device_id")
    device_type = data.get("device_type")
    supported_sensors = data.get("sensors")
    supported_actuators = data.get("actuators")
    
    # check if device_type and device_id are provided
    if device_type == None or device_id == None:
        auth_logger.error("Recieved request with missing device_type or device_id")
        response = {"error": "device_type and device_id (mac-address) are required"}
        return jsonify(response), 400
    
    # check if the provided device_type is valid
    if device_type not in ['sensor-device', 'actuator-device', 'client-device']:
        auth_logger.error("Recieved request with invalid device_type")
        response = {"error": "invalid device-type - has to be one of 'sensor-device', 'actuator-device', 'client-device'"}
        return jsonify(response), 400
    
    # check if device_id is a valid mac-address
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$" , device_id.lower()) == None:
        auth_logger.error("Recieved request with invalid mac-address")
        response = {"error": "invalid device_id - has to be a valid mac-address"}
        return jsonify(response), 400
    
    device_id = device_id.lower()
    
    #################################
    # REGISTER DEVICE IN DATABASE
     
    with db_handler() as db:
        # check database if device is already known    
        is_known_device = None
        try:
            is_known_device = db.is_known_device(device_id)
        except Exception as e:
            auth_logger.error(f"Something went wrong while checking if device is known <{e}>")
            return jsonify({"error": "internal server error"}), 500
        
        #################################
        # CASE: device is already known
        if is_known_device:
            # update ip address
            try:
                db.update_ip_address(device_id, request.remote_addr)
                auth_logger.debug(f"Updated ip address of device <{device_id}> to <{request.remote_addr}>")
            except Exception as e:
                auth_logger.error(f"Something went wrong while updating ip address <{e}>")
                return jsonify({"error": "internal server error"}), 500
            
            # send back api key of device
            try:
                api_key = db.get_api_key(device_id)
                return jsonify({"api_key": api_key}), 200
            except Exception as e:
                auth_logger.error(f"Something went wrong while getting api key <{e}>") 
                return jsonify({"error": "internal server error"}), 500
        
        #################################
        # CASE: device is not known yet
        else:
            api_key = f"{secrets.token_urlsafe(16)}"
            ip_address = request.remote_addr
            
            #################################
            # CLIENT DEVICE
            if "client-device" == device_type:
                try:
                    db.add_client_device(api_key, device_id, ip_address)
                    auth_logger.debug(f"Added client device <{device_id}> [<{ip_address}>] with api key <{api_key}>")
                    return jsonify({"api_key": api_key}), 200
                except Exception as e:
                    auth_logger.error(f"Something went wrong while adding client device <{e}>")
                    return jsonify({"error": "internal server error"}), 500

            #################################
            # SENSOR DEVICE
            elif "sensor-device" == device_type:
                if supported_sensors == None:
                    auth_logger.error("Recieved sensor auth request with missing sensor list") 
                    return jsonify({"error": "sensor list not specified"}), 400
                
                try:
                    db.add_sensor_device(api_key, device_id, ip_address, supported_sensors)
                    auth_logger.debug(f"Added sensor device <{device_id}> [<{ip_address}>] with api key <{api_key}>")
                    return jsonify({"api_key": api_key}), 200
                except Exception as e:
                    auth_logger.error(f"Something went wrong while adding sensor device <{e}>")
                    return jsonify({"error": "internal server error"}), 500
                
            #################################
            # ACTUATOR DEVICE
            elif "actuator-device" == device_type:
                if supported_actuators == None:
                    auth_logger.error("Recieved actuator auth request with missing actuator list") 
                    return jsonify({"error": "actuator list not specified"}), 400
                
                try:
                    db.add_actuator_device(api_key, device_id, ip_address, supported_actuators)
                    auth_logger.debug("Added actuator device <{device_id}> [<{ip_address}>] with api key <{api_key}>")
                    return jsonify({"api_key": api_key}), 200
                except Exception as e:
                    auth_logger.error(f"Something went wrong while adding actuator device <{e}>")
                    return jsonify({"error": "internal server error"}), 500
            
            #################################
            # DEFAULT CASE   
            else:
                auth_logger.error("Something went wrong while adding device - this should never happen")
                return jsonify({"error": "internal server error"}), 500
            
            