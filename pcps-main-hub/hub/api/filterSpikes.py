import numpy as np
from database.database_setup import db_handler

schwellenwertMultiplikator = {"ph": 2.00, "ec": 2.00, "waterlevel": 2.00, "temperature": 2.00, "humidity": 2.00, "light": 2.00}
time_interval              = {"ph": 900,   "ec": 900,   "waterlevel": 900,   "temperature": 900,   "humidity": 900,   "light": 900}
waterlevel_stuff           = {"number_of_consectutive_empties": 5, "counter": 0}

def is_spike(sensor_type, historic_data, value):
    # use IQR to detect spikes
    historic_data = np.sort(historic_data)

    q1 = np.percentile(historic_data, 25)
    q3 = np.percentile(historic_data, 75)

    iqr = q3 - q1

    multiplikator = schwellenwertMultiplikator[sensor_type]

    lower_bound = q1 - multiplikator * iqr
    upper_bound = q3 + multiplikator * iqr

    if upper_bound < lower_bound:
        tmp = upper_bound
        upper_bound = lower_bound
        lower_bound = tmp

    if lower_bound <= value <= upper_bound:
        return False
    else:
        return True
    
def getHistoryData(sensor_type, column, interval):
    with db_handler() as db:
        data = db.getHistory(sensor_type, column, interval)
        return data
 
def spike_detected(sensor_type, data):
    match(sensor_type):
        case "ph":
            history = getHistoryData(sensor_type, "ph", time_interval[sensor_type])
            if history == None or len(history) <= 16:
                return False
            
            incoming_value = data['ph']
            
            return is_spike(sensor_type, history, incoming_value)
        
        case "ec":
            history = getHistoryData(sensor_type, "ec", time_interval[sensor_type])
            if history == None or len(history) <= 16:
                return False
            
            incoming_value = data['ec']
            
            return is_spike(sensor_type, history, incoming_value)
        
        case "waterlevel":
            # check if the waterlevel is empty for a certain amount of time (5 times in a row)
            incoming_value = data['waterlevel']
            water_full = 0
            
            if incoming_value == water_full:
                waterlevel_stuff["counter"] = 0
                return True
            else:
                waterlevel_stuff["counter"] += 1
                
                if waterlevel_stuff["counter"] >= waterlevel_stuff["number_of_consectutive_empties"]:
                    return False
                else:
                    return True
            
        case "temperature":
            history = getHistoryData(sensor_type, "temperature", time_interval[sensor_type])
            if history == None or len(history) <= 16:
                return False
            
            incoming_value = data['temperature']
            
            return is_spike(sensor_type, history, incoming_value)
        
        case "humidity":
            history = getHistoryData(sensor_type, "humidity", time_interval[sensor_type])
            if history == None or len(history) <= 16:
                return False
            
            incoming_value = data['humidity']
            
            return is_spike(sensor_type, history, incoming_value)
        
        case "light":
            history_visible = getHistoryData(sensor_type, "visible", time_interval[sensor_type])
            history_ir = getHistoryData(sensor_type, "ir", time_interval[sensor_type])
            history_uv = getHistoryData(sensor_type, "uv", time_interval[sensor_type])
            
            if history_visible == None or len(history_visible) <= 16:
                return False
            if history_ir == None or len(history_ir) <= 16:
                return False
            if history_uv == None or len(history_uv) <= 16:
                return False
            
            incoming_visible = data['visible']
            incoming_ir = data['ir']
            incoming_uv = data['uv']
            
            is_spike_visible = is_spike(sensor_type, history_visible, incoming_visible)
            is_spike_ir = is_spike(sensor_type, history_ir, incoming_ir)
            is_spike_uv = is_spike(sensor_type, history_uv, incoming_uv)
            
            return is_spike_visible or is_spike_ir or is_spike_uv
        
        case _:
            raise Exception("Sensor type not found")
