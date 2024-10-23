from flask import Blueprint, request, jsonify
from flask_cors import CORS
import requests, json


from database.database_setup import DatabaseHandler

log_bp = Blueprint('log', __name__, url_prefix='/api/log')
CORS(log_bp, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Documentation:
# parameter: data: list
# return: json
# what it does: converts the data to json
def data_to_json(data):
    result_json = {'data': []}

    dataset_list = [{'timestamp': data['timestamp'], 'statuscode': data['statuscode'], 'sensor_type': data['sensor_type']} for data in data]
    result_json['data']=(dataset_list)

    return json.dumps(result_json, indent=2)

# Documentation:
# parameter: -
# return: json
# what it does: gets the logs from the database
@log_bp.route('', methods=['GET'])
def get_logs():
    db = DatabaseHandler()

    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sensorType = request.args.get('sensorType', default=None, type=str)

    try:
        data = db.get_logs(limit, offset, sensorType)

        data = data_to_json(data)
        return (data, 200)
    except Exception as e:
        return jsonify({"error": "couldn't fetch logs from database"}), 400

    
