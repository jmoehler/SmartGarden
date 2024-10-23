from flask import Blueprint, jsonify, request
from flask_login import login_required
import logging
import os
from glob import glob

liveimage_get_bp = Blueprint('liveimage_get', __name__, url_prefix='')

logger = logging.getLogger('BACKEND(liveimage_get)')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(sh)


#################################################################
#
#   IMAGE ROUTES
#
#################################################################

@liveimage_get_bp.route('/get_image_path' , methods=['GET'])
@login_required
def get_latest_image_path():
    
    logger.info(os.getcwd())


    directory='./webserver/static/pictures/plant'

    try:
        if not os.path.exists(directory):
            logger.error(f"Directory '{directory}' does not exist.")
            logger.error("No images found in the directory.")
            return None

        image_files = glob(os.path.join(directory, '*.jpg'))

        if not image_files:
            logger.warning("No images found in the directory.")
            return None

        latest_image_path = max(image_files, key=os.path.getmtime)
        latest_image_path = latest_image_path.replace("\\", "/")
        latest_image_path = latest_image_path.replace("./webserver", "")

        logger.info(f"Latest image path: {latest_image_path}")
        return jsonify({
        'image_path': latest_image_path
        })


    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify(error="An error occurred"), 500