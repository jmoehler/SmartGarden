from flask import Blueprint, render_template
from flask_login import login_required

configs_bp = Blueprint('configs', __name__, url_prefix='')

#################################################################
#
#   CONFIGS ROUTES
#
#################################################################

@configs_bp.route('/configs', methods=['POST', 'GET'])
@login_required
def configs():  
    return render_template('configs.html')