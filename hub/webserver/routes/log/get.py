from flask import Blueprint, jsonify, redirect
from flask_login import login_required

from database.database_setup import db_handler

log_get_bp = Blueprint('log_get', __name__, url_prefix='')

#################################################################
#
#   LOG ROUTES
#
#################################################################
@log_get_bp.route('/get_all_logs', methods=['GET'])
def get_log_full():
    with db_handler() as db:
        log = db.get_all_logs()
        return jsonify({'log': log})

@log_get_bp.route('/delete_all_logs', methods=['POST'])
def delete_log_full():
    with db_handler() as db:
        db.delete_all_logs()
        return redirect('/log')