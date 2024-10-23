from flask import Blueprint, request, jsonify
from flask_cors import CORS
import requests
import logging

from database.database_setup import db_handler

# configure logging
actuators_logger = logging.getLogger('API(ACTUATORS)')
actuators_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
actuators_logger.addHandler(sh)


actuators_bp = Blueprint('actuators', __name__, url_prefix='/api/actuators')
CORS(actuators_bp, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@actuators_bp.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store')
    return response

@actuators_bp.route('<actuator_type>', methods=['GET'])
def get_actuator_status(actuator_type):
    with db_handler as db:
        api_key = request.headers.get("Authorization")
        
        if api_key == None:
            actuators_logger.error("Recieved request with no Authorization header")
            return jsonify({"error": "no Authorization header"}), 400

        authorized, _, device_type = None, None, None
        
        try:
            authorized, _, device_type = db.check_authorization(api_key)
        except Exception as e:
            actuators_logger.error(f"Something went wrong while checking authorization <{e}>")
            return jsonify({"error": "internal server error"}), 500

        if not authorized:
            actuators_logger.error("Unauthorized request")
            return jsonify({"error": "unauthorized"}), 401
        
        if device_type != "client-device":
            actuators_logger.error("Method not allowed")
            return jsonify({"error": "method not allowed"}), 405

        if actuator_type not in ["led", "waterpump", "ecpump", "phpump"]:
            actuators_logger.error("Actuator not supported")
            return jsonify({"error": "actuator not supported"}), 404
        
        
        connections = None
        
        try:
            connections = db.get_actuator_connection_details(actuator_type)
        except:
            actuators_logger.error("Something went wrong while getting actuator connection details")
            return jsonify({"error": "actuator connection details not found"}), 500
        
        for (api_key, ip_address) in connections:
            try:
                response = requests.get(f"http://{ip_address}:6000/api/{actuator_type}", headers={"Authorization": api_key}, timeout=1)
                if response.status_code == 200:
                    return jsonify(response.json()), 200
                else:
                    actuators_logger.error(f"Recieved response with status code {response.status_code}")
                    pass 
            except:
                actuators_logger.error("Something went wrong while requesting actuator status")
                continue
        
        actuators_logger.error("Currently no actuator responded to the request")
        return jsonify({"error": "Something went wrong while requesting actuator status"}), 500
    

@actuators_bp.route('<actuator_type>', methods=['POST'])
def toggle_actuator(actuator_type):
    with db_handler as db:
        api_key = request.headers.get("Authorization")
        
        if api_key == None:
            actuators_logger.error("Recieved request with no Authorization header")
            return jsonify({"error": "no Authorization header"}), 400
        
        authorized, _, device_type = None, None, None
        
        try:
            authorized, _, device_type = db.check_authorization(api_key)
        except Exception as e:
            actuators_logger.error(f"Something went wrong while checking authorization <{e}>")
            return jsonify({"error": "internal server error"}), 500
        
        if not authorized:
            actuators_logger.error("Unauthorized request")
            return jsonify({"error": "unauthorized"}), 401
        
        if device_type != "client-device":
            actuators_logger.error("Method not allowed")
            return jsonify({"error": "method not allowed"}), 405

        if actuator_type not in ["led", "waterpump", "ecpump", "phpump"]:
            actuators_logger.error("Actuator not supported")
            return jsonify({"error": "actuator not supported"}), 404
        
        connections = None
        
        try:
            connections = db.get_actuator_connection_details(actuator_type)
        except:
            actuators_logger.error("Something went wrong while getting actuator connection details")
            return jsonify({"error": "actuator connection details not found"}), 500
        
        
        data = None
        try:
            data = request.get_json()
            toggle_to = data.get("toggle")
            if toggle_to == None or toggle_to not in ["on", "off"]:
                actuators_logger.error("Invalid toggle data")
                return jsonify({"error": "invalid toggle data"}), 400
            
            for (api_key, ip_address) in connections:
                try:
                    response = requests.post(f"http://{ip_address}:6000/api/{actuator_type}", headers={"Authorization": api_key}, json={"toggle": toggle_to}, timeout=1)
                    if response.status_code == 200:
                        return jsonify(response.json()), 200
                    else:
                        actuators_logger.error(f"Recieved response with status code {response.status_code}")
                        pass 
                except:
                    actuators_logger.error("Something went wrong while requesting actuator status")
                    continue
            
            actuators_logger.error("Currently no actuator responded to the request")
            return jsonify({"error": "Something went wrong while requesting actuator status"}), 500
        except:
            for (api_key, ip_address) in connections:
                try:
                    response = requests.post(f"http://{ip_address}:6000/api/{actuator_type}", headers={"Authorization": api_key}, timeout=1)
                    if response.status_code == 200:
                        return jsonify(response.json()), 200
                    else:
                        actuators_logger.error(f"Recieved response with status code {response.status_code}")
                        pass 
                except:
                    actuators_logger.error("Something went wrong while requesting actuator status")
                    continue
            
            actuators_logger.error("Currently no actuator responded to the request")
            return jsonify({"error": "Something went wrong while requesting actuator status"}), 500
        
        

        