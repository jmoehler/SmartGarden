from flask import Blueprint, jsonify
from flask_login import login_required

from database.database_setup import db_handler

ranges_get_bp = Blueprint('ranges_get', __name__, url_prefix='')


#################################################################
#
#   RANGES GET ROUTES
#
#################################################################


# returns template name of active template
@ranges_get_bp.route('/get_active_template_name', methods=['GET'])
@login_required
def get_active_template_name():
    with db_handler() as db:
        template_name = db.get_active_template_name()
        return jsonify({"template_name": template_name})


# the following routes return the ranges for a specific sensor
# TODO: probably more convenient to compress functionality into a single route, instead of routes for each sensor
@ranges_get_bp.route('/get_light_range', methods=['GET'])
@login_required
def get_light_range():
    with db_handler() as db:
        ranges = db.get_range('light')
        return jsonify({ 'light': ranges })

@ranges_get_bp.route('/get_humidity_range', methods=['GET'])
@login_required
def get_humidity_range():
    with db_handler() as db:
        ranges = db.get_range('hum')
        return jsonify({ 'humidity': ranges })

@ranges_get_bp.route('/get_ph_range', methods=['GET'])
@login_required
def get_ph_range():
    with db_handler() as db:
        ranges = db.get_range('ph')
        return jsonify({ 'ph': ranges })

@ranges_get_bp.route('/get_ec_range', methods=['GET'])
@login_required
def get_ec_range():
    with db_handler() as db:
        ranges = db.get_range('ec')
        return jsonify({ 'ec': ranges })

@ranges_get_bp.route('/get_temperature_range', methods=['GET'])
@login_required
def get_temperature_range():
    with db_handler() as db:
        ranges = db.get_range('temp')
        return jsonify({ 'temperature': ranges })

