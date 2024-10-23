from flask import Flask, request, jsonify
import secrets
import time
import requests
import random

import logging

#configure logging
actsim_logger = logging.getLogger('SIM(ACTUATORS)')
actsim_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('sim_actuators.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)

fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

actsim_logger.addHandler(fh)
actsim_logger.addHandler(sh)


from enviroment import *

app = Flask(__name__)
api_key = None
hub_url = "http://127.0.0.1:8000"

status = {"led":"on"}

@app.route('/api/led', methods=['GET'])
def getValues():
    request_key = request.headers.get("Authorization")
      
    if request_key != api_key:
        response = {"error": "unauthorized"}
        return jsonify(response), 401
    
    actStatus = status["led"]
    response = jsonify({'status': actStatus})
    return response, 200

@app.route('/api/led', methods=['POST'])
def setValueLED():
    request_key = request.headers.get("Authorization")
    
    if request_key != api_key:
        response = {"error": "unauthorized"}
        return jsonify(response), 401
    
    data = request.get_json()
    toggle_to = data.get("toggle")
    if toggle_to == None or toggle_to not in ["on", "off"]:
        response = {"error": "toggle not specified"}
        return jsonify(response), 400
    
    status["led"] = toggle_to
    actStatus = status["led"]

    actsim_logger.info(f"LED toggled to {toggle_to}")
    
    response = jsonify({'status': actStatus})
    return response, 200

@app.route('/api/waterpump', methods=['POST'])
def toggleWaterpump():
    request_key = request.headers.get("Authorization")
    
    if request_key != api_key:
        response = {"error": "unauthorized"}
        return jsonify(response), 401
    
    # the waterpump would fill the tank with water
    decrease_ec()
    
    actsim_logger.info(f"Waterpump toggled - EC decreased")

    response = jsonify({'success': "toggled"})
    return response, 200

@app.route('/api/ecpump', methods=['POST'])
def toggleECpump():
    request_key = request.headers.get("Authorization")
    
    if request_key != api_key:
        response = {"error": "unauthorized"}
        return jsonify(response), 401
    
    # the ecpump would fill the tank with fertilizer 
    # for a certain amount of time
    increase_ec()
    
    actsim_logger.info(f"EC pump toggled - increased EC")
    
    response = jsonify({'success': "toggled"})
    return response, 200

@app.route('/api/phpump', methods=['POST'])
def togglePHpump():
    request_key = request.headers.get("Authorization")
    
    if request_key != api_key:
        response = {"error": "unauthorized"}
        return jsonify(response), 401
    
    # the phpump would fill the tank with ph-liquid
    # for a certain amount of time
    increase_ph()
    
    actsim_logger.info(f"PH pump toggled - increased PH")
    
    response = jsonify({'success': "toggled"})
    return response, 200

def init():
    response = requests.post(f"{hub_url}/api/authenticate", json={"device_type": "actuator-device", "device_id": "98:87:76:65:54:43", "actuators": ["led", "waterpump", "ecpump", "phpump"]}, timeout=1)
    key = response.json().get("api_key")
    
    return key

if __name__ == '__main__':
    api_key = init()
    app.run(host='127.0.0.1', port=6000, debug=True, use_reloader=False)