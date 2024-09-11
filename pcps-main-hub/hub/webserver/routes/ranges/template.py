from flask import Blueprint, render_template, request, redirect, jsonify
from flask_login import login_required
import datetime
from datetime import timedelta

from database.database_setup import db_handler

template_bp = Blueprint('template', __name__, url_prefix='')

#################################################################
#
#   TEMPLATE (EDIT, DELETE, ADD, CHANGE ACTIVE)
#
#################################################################

# returns list of template names
@template_bp.route('/get_all_template_names', methods=['GET'])
@login_required
def get_all_templates_names ():
    with db_handler() as db:
        templates = db.get_all_template_names()
        return jsonify({'template_names': templates})

@template_bp.route('/get_all_templates', methods=['GET'])
@login_required
def get_all_templates():
    try:
        with db_handler() as db:
            templates = db.get_all_templates()
            templates_as_objects = []
            for row in templates:
                row_object = { 
                    'id': row[0],
                    'template_name': row[1],
                    'active': row[2],
                    'light_on': str(row[3]),
                    'light_off': str(row[4]), 
                    'temp_min': row[5],
                    'temp_max': row[6],
                    'hum_min': row[7],
                    'hum_max': row[8],
                    'ph_min': row[9],
                    'ph_max': row[10],
                    'ec_min': row[11],
                    'ec_max': row[12]
                }
                templates_as_objects.append(row_object)

        response_data = {'templates': templates_as_objects}

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# adds a template to the database
@template_bp.route('/add_template', methods=['POST'])
@login_required
def add_template():
    with db_handler() as db:
        ph_range_start = float(request.form.get('ph-form-min'))
        ph_range_end = float(request.form.get('ph-form-max'))
        
        ec_range_start = float(request.form.get('ec-form-min'))
        ec_range_end = float(request.form.get('ec-form-max'))
        
        temperature_range_start = int(request.form.get('temperature-form-min'))
        temperature_range_end = int(request.form.get('temperature-form-max'))
        
        humidity_range_start = int(request.form.get('humidity-form-min'))
        humidity_range_end = int(request.form.get('humidity-form-max'))
        
        light_range_start = request.form.get('light-form-min')
        light_range_end = request.form.get('light-form-max')
        
        light_range_start = datetime.time(int(light_range_start.split(':')[0]), int(light_range_start.split(':')[1]), 0)
        light_range_end = datetime.time(int(light_range_end.split(':')[0]), int(light_range_end.split(':')[1]), 0)

        template_name = request.form.get('templatename-form')
        template_names = db.get_all_template_names()
        default_name = "New Template"

        # adapt default name if there is template with this name
        if template_names:
            for count in range(len(template_names)):
                if default_name in template_names:
                    default_name = f"New Template {count + 1}"
        
        if not template_name:
            template_name = default_name

        # add default ranges to the database
        db.add_ranges(
            ph_min=ph_range_start, ph_max=ph_range_end,
            ec_min=ec_range_start, ec_max=ec_range_end,
            temp_min=temperature_range_start, temp_max=temperature_range_end,
            hum_min=humidity_range_start, hum_max=humidity_range_end,
            light_on=light_range_start, light_off=light_range_end,
            template_name=template_name
        )
        return render_template('home.html')
    

@template_bp.route('/delete_templates', methods=['POST'])
@login_required
def delete_template():
    with db_handler() as db:
        checked_templates = request.form.getlist('inputs')
        for template in checked_templates:
            db.delete_template(template_name=template)
                               
    return render_template('home.html')

# updates a template in the database
@template_bp.route('/edit_template', methods=['POST'])
@login_required
def edit_template():
    ph_min = request.form.get('ph-range-min')
    ph_max = request.form.get('ph-range-max')    
    ec_min = request.form.get('ec-range-min')
    ec_max = request.form.get('ec-range-max') 
    temp_min = request.form.get('temp-range-min')
    temp_max = request.form.get('temp-range-max')
    humidity_min = request.form.get('humidity-range-min')
    humidity_max = request.form.get('humidity-range-max')   
    light_min = request.form.get('light-range-min')
    light_max = request.form.get('light-range-max')
    template_name = request.form.get('template-name')

    try:
        ph_min = float(ph_min)
        ph_max = float(ph_max)
        ec_min = float(ec_min)
        ec_max = float(ec_max)
        temp_min = int(temp_min)
        temp_max = int(temp_max)
        humidity_min = int(humidity_min)
        humidity_max = int(humidity_max)
        light_min = datetime.time(4, 0, 0)
        light_max = datetime.time(16, 0, 0)
        template_name = str(template_name)
    except:
        return render_template('configs.html')
        
    
    with db_handler() as db:
        db.update_active_ranges(
            light_on = light_min,
            light_off = light_max,
            temp_min = temp_min,
            temp_max = temp_max,
            hum_min=humidity_min,
            hum_max=humidity_max,
            ph_min=ph_min,
            ph_max=ph_max,
            ec_min=ec_min,
            ec_max=ec_max,
            template_name=template_name
        )
        
        return redirect('/configs')


@template_bp.route('/activate_template', methods=['POST'])
def setActiveTemplate():
    template = request.form.getlist('inputs')[0]
    with db_handler() as db:
        if template:
            db.activate_template(template)
        
        return render_template('home.html')


# changes active template in database
# @template_bp.route('/change_active_template', methods=['POST'])
# @login_required
# def change_active_template():
#     selected_template = request.form.get('selected_template', None)

#     if selected_template is not None:
#         with db_handler() as db:
#             db.change_active_template(selected_template)

#     return redirect('/configs')