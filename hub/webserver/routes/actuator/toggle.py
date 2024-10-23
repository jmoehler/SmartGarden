from flask import Blueprint, jsonify, request
from flask_login import login_required
import requests
import logging

from database.database_setup import db_handler

logger = logging.getLogger('BACKEND(actuator_toggle)')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(sh)

actuator_toggle_bp = Blueprint('actuator_toggle', __name__, url_prefix='')

#################################################################
#
#   ACTUATOR TOGGLE ROUTES
#
#################################################################

@actuator_toggle_bp.route('/toggle_led', methods=['POST'])
@login_required
def toggle_led():
    with db_handler() as db:
        connections = None
        
        try:
            connections = db.get_actuator_connection_details("led")
        except:
            logger.error("Something went wrong while getting actuator connection details")
            return jsonify({"error": "no such actuator currently available"}), 500
        
        # try every connection until one succeeds
        for (api_key, ip_address) in connections:
            try:
                logger.info(f"Trying to toggle led at {ip_address} with api key {api_key}")
                response = requests.post(f"http://{ip_address}:6000/api/led", headers={"Authorization": api_key}, json=request.get_json(), timeout=1)
                logger.info(f"Trying to toggle led at {ip_address} with api key {api_key} - {response}")
                if response.status_code == 200:
                    return jsonify(response.json()), 200
                else:
                    logger.error("Something went wrong while requesting actuator status")
                    logger.error(response.status_code(), response.json())
            except:
                pass
        
        logger.error("Currently no actuator available responding to this request")
        return jsonify({"error": "something went wrong while requesting actuator status"}), 500

@actuator_toggle_bp.route('/toggle_waterpump', methods=['POST'])
@login_required
def toggle_waterpump():
    with db_handler() as db:
        connections = None
        
        try:
            connections = db.get_actuator_connection_details("waterpump")
        except:
            logger.error("Something went wrong while getting actuator connection details")
            return jsonify({"error": "no such actuator currently available"}), 500
        
        # try every connection until one succeeds
        for (api_key, ip_address) in connections:
            try:
                response = requests.post(f"http://{ip_address}:6000/api/waterpump", headers={"Authorization": api_key}, timeout=1)
                if response.status_code == 200:
                    return jsonify(response.json()), 200
                else:
                    logger.error("Something went wrong while requesting actuator status")
                    logger.error(response.status_code(), response.json())
            except:
                pass
        
        logger.error("Currently no actuator available responding to this request")
        return jsonify({"error": "something went wrong while requesting actuator status"}), 500

@actuator_toggle_bp.route('/toggle_ecpump', methods=['POST'])
@login_required
def toggle_ecpump():
    with db_handler() as db:
        connections = None
        
        try:
            connections = db.get_actuator_connection_details("ecpump")
        except:
            logger.error("Something went wrong while getting actuator connection details")
            return jsonify({"error": "no such actuator currently available"}), 500
        
        # try every connection until one succeeds
        for (api_key, ip_address) in connections:
            try:
                response = requests.post(f"http://{ip_address}:6000/api/ecpump", headers={"Authorization": api_key}, timeout=1)
                if response.status_code == 200:
                    return jsonify(response.json()), 200
                else:
                    logger.error("Something went wrong while requesting actuator status")
                    logger.error(response.status_code(), response.json())
            except:
                pass
        
        logger.error("Currently no actuator available responding to this request")
        return jsonify({"error": "something went wrong while requesting actuator status"}), 500

@actuator_toggle_bp.route('/toggle_phpump', methods=['POST'])
@login_required
def toggle_phpump():
    with db_handler() as db:
        connections = None
        
        try:
            connections = db.get_actuator_connection_details("phpump")
        except:
            logger.error("Something went wrong while getting actuator connection details")
            return jsonify({"error": "no such actuator currently available"}), 500
        
        # try every connection until one succeeds
        for (api_key, ip_address) in connections:
            try:
                response = requests.post(f"http://{ip_address}:6000/api/phpump", headers={"Authorization": api_key}, timeout=1)
                if response.status_code == 200:
                    return jsonify(response.json()), 200
                else:
                    logger.error("Something went wrong while requesting actuator status")
                    logger.error(response.status_code(), response.json())
            except:
                pass
        
        logger.error("Currently no actuator available responding to this request")
        return jsonify({"error": "something went wrong while requesting actuator status"}), 500
