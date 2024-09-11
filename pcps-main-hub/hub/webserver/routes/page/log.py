from flask import Blueprint, render_template
from flask_login import login_required

log_bp = Blueprint('log', __name__, url_prefix='')

#################################################################
#
#   LOG ROUTES
#
#################################################################
@log_bp.route('/log', methods=['GET'])
@login_required
def log():
    return render_template('log.html')
