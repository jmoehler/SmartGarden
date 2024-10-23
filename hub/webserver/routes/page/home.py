from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

home_bp = Blueprint('home', __name__, url_prefix='')

#################################################################
#
#  HOME PAGE
#
#################################################################

@home_bp.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return render_template('home.html', username=current_user.id)
    else:
        return redirect(url_for('login'))
    
@home_bp.route('/home', methods=['POST', 'GET'])
@login_required
def home_page():
    return render_template('home.html')