from flask import Blueprint, jsonify, request
from flask_login import login_required
import requests
import logging

from database.database_setup import db_handler

logger = logging.getLogger('BACKEND(actuator_status)')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(sh)

actuator_status_bp = Blueprint('actuator_status', __name__, url_prefix='')



#################################################################
#
#   ACTUATOR STATUS ROUTES
#
#################################################################

@actuator_status_bp.route('/get_led_status', methods=['GET'])
@login_required
def get_led_status():
    with db_handler() as db:
        connections = None
        
        try:
            connections = db.get_actuator_connection_details("led")
        except Exception as e:
            logger.error(f"Something went wrong while getting actuator connection details <{e}>")
            return jsonify({"error": "no such actuator currently available"}), 500
        
        # try every connection until one succeeds
        for (api_key, ip_address) in connections:
            try:
                response = requests.get(f"http://{ip_address}:6000/api/led", headers={"Authorization": api_key}, timeout=1)
                if response.status_code == 200:
                    return jsonify(response.json()), 200
                else:
                    logger.error(f"Something went wrong (<{response.status_code}>)while requesting actuator status at {ip_address} with api key {api_key}")
                    logger.error(response.status_code(), response.json())
            except:
                pass
        
        logger.error("Currently no actuator available responding to this request")
        return jsonify({"error": "something went wrong while requesting actuator status"}), 500
