from flask import Blueprint, jsonify
from flask_login import login_required

from database.database_setup import db_handler

analysis_get_bp = Blueprint('analysis_get', __name__, url_prefix='')

#################################################################
#
#   PICTURE ANALYSIS ROUTES
#
#################################################################
    
@analysis_get_bp.route('/get_picture_analysis', methods=['GET'])
@login_required
def get_picture_analysis():
    try:
        with db_handler() as db:
            analysis = db.get_most_recent_picture_analysis()
            if analysis:
                picture_path = analysis['picture_path']
                result = analysis['result']
                probability = analysis['probability']
                recommendation = analysis['recommended_action']  # Korrigierter Schlüssel
                
                return jsonify(
                    picture_path=picture_path,
                    result=result,
                    probability=probability,
                    recommendation=recommendation  # Korrigierter Schlüssel
                )
            return jsonify({"error": "no picture analysis available"}), 404
    except:
        return jsonify({"error": "Something went wrong while getting picture analysis"}), 500