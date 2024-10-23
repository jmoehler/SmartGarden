from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import bcrypt

from database.database_setup import db_handler

login_manager = LoginManager()
login_bp = Blueprint('login', __name__, url_prefix='')

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    with db_handler() as db:
        if db.user_exists(username):
            return User(username)
        else:
            return None

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        plain_password = request.form['password']
        email = request.form['email']
        
        with db_handler() as db:
            if db.user_exists(username):
                return render_template('register.html', error='Username already exists.')
            else:
                hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
                db.add_user(username, email, hashed_password.decode('utf-8'))
            
        return redirect(url_for('login'))

    return render_template('register.html')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with db_handler() as db:
            hashed_password = db.get_password(username)
            if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                user = User(username)
                login_user(user)
                return redirect(url_for('home.home'))
            else:
                return render_template('login.html', error='Wrong username or password.')
        
    return render_template('login.html')

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

