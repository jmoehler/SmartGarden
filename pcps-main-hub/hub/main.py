
import os
import bcrypt
    
from database.database_setup import db_handler

#################################################################
#
#   WEBSERVER SETUP
#
#################################################################
import logging

app_logger = logging.getLogger('HUB')
app_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app_logger.addHandler(sh)

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from webserver.api.authenticate import authenticate_bp
from webserver.api.sensors import sensors_bp
from webserver.api.actuators import actuators_bp
from webserver.api.log import log_bp
from webserver.routes.sensordata.get import sensordata_get_bp
from webserver.routes.analysis.get import analysis_get_bp
from webserver.routes.actuator.toggle import actuator_toggle_bp
from webserver.routes.actuator.status import actuator_status_bp
from webserver.routes.log.get import log_get_bp
from webserver.routes.ranges.get import ranges_get_bp
from webserver.routes.ranges.template import template_bp
from webserver.routes.liveimage.get import liveimage_get_bp
from webserver.routes.history.get import history_get_bp
from webserver.routes.page.log import log_bp
from webserver.routes.page.configs import configs_bp
from webserver.routes.page.home import home_bp

app = Flask(__name__, template_folder='./webserver/templates', static_folder='./webserver/static')
app.secret_key = os.urandom(24)

app.register_blueprint(authenticate_bp)
app.register_blueprint(sensors_bp)
app.register_blueprint(actuators_bp)
app.register_blueprint(sensordata_get_bp)
app.register_blueprint(analysis_get_bp)
app.register_blueprint(actuator_toggle_bp)
app.register_blueprint(actuator_status_bp)
app.register_blueprint(log_get_bp)
app.register_blueprint(ranges_get_bp)
app.register_blueprint(template_bp)
app.register_blueprint(liveimage_get_bp)
app.register_blueprint(history_get_bp)
app.register_blueprint(log_bp)
app.register_blueprint(configs_bp)
app.register_blueprint(home_bp)

#################################################################
#
#   LOGIN MANAGER AND ROUTE SETUP
#
#################################################################
login_manager = LoginManager(app)
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

@app.route('/register', methods=['GET', 'POST'])
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

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    #################################################################
    #
    #   mDNS SERVICE REGISTRATION
    #
    #################################################################
    from zeroconf import Zeroconf, ServiceInfo
    import socket

    app_logger.info('Registering mDNS service')
    service_type = '_http._tcp.local.'
    service_name = "PlantHub._http._tcp.local."
    port = 8000

    # ip address extraction
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # connect to googles public DNS server
    ip_address = s.getsockname()[0]
    s.close()
    ip_address
    
    zeroconf = Zeroconf()
    
    info = ServiceInfo(type_=service_type,name=service_name,port=port,weight=0,priority=0,addresses=[socket.inet_aton(ip_address)])
    zeroconf.register_service(info)

    #################################################################
    #
    #   CAMERA AND AUTOCONTROLLER THREAD SETUP
    #
    #################################################################
    import threading
    import argparse
    import platform
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auto', action='store_true', help='enable auto mode')
    parser.add_argument('-c', '--camera', action='store_true', help='enable camera')
    args = parser.parse_args()
    
    if args.camera:
        app_logger.info('Starting camera thread')
        from webserver.camera import ImageCapture
        from webserver.camera_not_raspberry import ImageCaptureNotRaspberry
        if platform.machine().startswith("aarch64") and platform.system() == "Linux":
            capture = ImageCapture()
        else:
            capture = ImageCaptureNotRaspberry()

        capture_thread = threading.Thread(target=capture.capture_and_manage_images)
        capture_thread.start()
        
    if args.auto:
        app_logger.info('Starting autocontroller thread')
        from control.autocontroller import AutoController
        autocontroller = AutoController()
        autocontroller_thread = threading.Thread(target=autocontroller.run)
        autocontroller_thread.start()

    #################################################################
    #
    #   WEBSERVER STARTUP
    #
    #################################################################
    app.run(debug=True, host='0.0.0.0', port=8000, use_reloader=False)