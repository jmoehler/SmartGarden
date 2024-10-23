import threading
import time
from database.database_setup import db_handler
from datetime import datetime, timedelta
import logging
import requests

# configure logging
control_logger = logging.getLogger('AUTOCONTROLLER')
control_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
control_logger.addHandler(sh)


class AutoController:
    def __init__(self):
        self.running = False
        
        self.ec_lock = threading.Lock()
        self.ph_lock = threading.Lock()
        self.light_lock = threading.Lock()
        self.water_lock = threading.Lock()
        
        self.waitingtime_ec = 3600          # = 1h
        self.waitingtime_ph = 3600          # = 1h
        self.waitingtime_light = 5          # = 5s
        self.waitingtime_water = 3600       # = 1h

    def pause(self):
        control_logger.info("Pausing autocontroller...")
        self.running = False

    def resume(self):
        control_logger.info("Restarting autocontroller...")
        self.running = True

    def run(self):
        control_logger.info("Starting autocontroller...")
        threading.Thread(target=self.regulate_ec).start()
        threading.Thread(target=self.regulate_ph).start()
        threading.Thread(target=self.regulate_light).start()
        threading.Thread(target=self.regulate_waterlevel).start()
        self.running = True

    def add_ec(self):
        with self.ec_lock:
            with db_handler() as db:
                connections = None
        
                try:
                    connections = db.get_actuator_connection_details("ecpump")
                except:
                    control_logger.error("Something went wrong while getting actuator connection details")
                    raise Exception("actuator connection details not found")
                
                # try every connection until one succeeds
                for (api_key, ip_address) in connections:
                    try:
                        response = requests.post(f"http://{ip_address}:6000/api/ecpump", headers={"Authorization": api_key}, timeout=1)
                        if response.status_code == 200:
                            return
                        else:
                            control_logger.error("Something went wrong while toggling actuator")
                            control_logger.error(response.status_code(), response.json())
                    except:
                        pass
                
                control_logger.error("Currently no actuator available responding to this request")
                raise Exception("Currently no actuator available responding to this request")
                
                
    def add_low_ph(self):
        with self.ph_lock:
            with db_handler() as db:
                connections = None
        
                try:
                    connections = db.get_actuator_connection_details("phpump")
                except:
                    control_logger.error("Something went wrong while getting actuator connection details")
                    raise Exception("actuator connection details not found")
                
                # try every connection until one succeeds
                for (api_key, ip_address) in connections:
                    try:
                        response = requests.post(f"http://{ip_address}:6000/api/phpump", headers={"Authorization": api_key}, timeout=1)
                        if response.status_code == 200:
                            return
                        else:
                            control_logger.error("Something went wrong while toggling actuator")
                            control_logger.error(response.status_code(), response.json())
                    except:
                        pass
                
                control_logger.error("Currently no actuator available responding to this request")
                raise Exception("Currently no actuator available responding to this request")
                

    def add_water(self):
        with self.water_lock:
            with db_handler() as db:
                connections = None
        
                try:
                    connections = db.get_actuator_connection_details("waterpump")
                except:
                    control_logger.error("Something went wrong while getting actuator connection details")
                    raise Exception("actuator connection details not found")
                
                # try every connection until one succeeds
                for (api_key, ip_address) in connections:
                    try:
                        response = requests.post(f"http://{ip_address}:6000/api/waterpump", headers={"Authorization": api_key}, timeout=1)
                        if response.status_code == 200:
                            return
                        else:
                            control_logger.error("Something went wrong while toggling actuator")
                            control_logger.error(response.status_code(), response.json())
                    except:
                        pass
                
                control_logger.error("Currently no actuator available responding to this request")
                raise Exception("Currently no actuator available responding to this request")

    def light_on(self):
        with self.light_lock:
            with db_handler() as db:
                connections = None
        
                try:
                    connections = db.get_actuator_connection_details("led")
                except:
                    control_logger.error("Something went wrong while getting actuator connection details")
                    raise Exception("actuator connection details not found")
                
                # try every connection until one succeeds
                for (api_key, ip_address) in connections:
                    try:
                        response = requests.post(f"http://{ip_address}:6000/api/led", headers={"Authorization": api_key}, json={"toggle": "on"}, timeout=1)
                        if response.status_code == 200:
                            return
                        else:
                            control_logger.error("Something went wrong while toggling actuator")
                            control_logger.error(response.status_code(), response.json())
                    except:
                        pass
                
                control_logger.error("Currently no actuator available responding to this request")
                raise Exception("Currently no actuator available responding to this request")

    def light_off(self):
        with self.light_lock:
            with db_handler() as db:
                connections = None
        
                try:
                    connections = db.get_actuator_connection_details("led")
                except:
                    control_logger.error("Something went wrong while getting actuator connection details")
                    raise Exception("actuator connection details not found")
                
                # try every connection until one succeeds
                for (api_key, ip_address) in connections:
                    try:
                        response = requests.post(f"http://{ip_address}:6000/api/led", headers={"Authorization": api_key}, json={"toggle": "off"}, timeout=1)
                        if response.status_code == 200:
                            return
                        else:
                            control_logger.error("Something went wrong while toggling actuator")
                            control_logger.error(response.status_code(), response.json())
                    except:
                        pass
                
                control_logger.error("Currently no actuator available responding to this request")
                raise Exception("Currently no actuator available responding to this request")
        
    def log_changed_state(self, sensor_type, last_state, current_state):
        sensor_type_mapping = {"ec": 1, "ph": 2}
         
        with db_handler() as db:
            if last_state == "too low" and current_state == "just right":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 1, sensor_type)
            elif last_state == "too low" and current_state == "too high":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 2, sensor_type)
            elif last_state == "just right" and current_state == "too low":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 3, sensor_type)
            elif last_state == "just right" and current_state == "too high":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 4, sensor_type)
            elif last_state == "too high" and current_state == "too low":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 5, sensor_type)
            elif last_state == "too high" and current_state == "just right":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 6, sensor_type)
                
    def log_critical_state(self, sensor_type, current_state):
        sensor_type_mapping = {"ec": 1, "ph": 2, "waterlevel": 3}
        
        with db_handler() as db:
            if current_state == "too low":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 7, sensor_type)
            elif current_state == "too high":
                db.add_log(sensor_type_mapping[sensor_type] * 100 + 8, sensor_type)

    def regulate_ec(self):
        last_state = None
        current_state = None
        same_state_counter = 0
        time_of_next_check = datetime.now() - timedelta(seconds=1)
        
        while True:
            if not self.running or datetime.now() < time_of_next_check:
                time.sleep(1)
                continue
            
            time_of_next_check = datetime.now() + timedelta(seconds=self.waitingtime_ec)
            
            control_logger.info("Checking EC...")
            try:
                with db_handler() as db:
                    min_value, max_value = db.get_range("ec")
                    sensor_data = db.get_sensor_data_most_recent("ec")

                    if sensor_data:
                        current_value = sensor_data[0]["ec_value"]
                        current_state = self.compare_with_range(current_value, min_value, max_value, "ec")

                        #################################################
                        # REGULATION LOGIC
                        #################################################
                        match current_state:
                            case "too low":
                                control_logger.warning("EC too low - adding fertilizer");
                                same_state_counter += 1
                                if same_state_counter < 5:
                                    self.add_ec()
                                else:
                                    self.log_critical_state("ec", current_state)
                            case "too high":
                                control_logger.warning("EC too high - adding water");
                                same_state_counter += 1
                                if same_state_counter < 5:
                                    self.add_water()
                                else:
                                    self.log_critical_state("ec", current_state)
                            case "just right":
                                same_state_counter = 0
                            case _:
                                control_logger.error("something went wrong while comparing ec value to range")
                                
                                
                        #################################################
                        # LAST STATE VS CURRENT STATE
                        #################################################
                        if last_state != current_state:
                            same_state_counter = 0
                            self.log_changed_state("ec", last_state, current_state)
                            
                        last_state = current_state
            except Exception as e:
                control_logger.error("something went wrong while regulating ec: " + str(e))

    def regulate_ph(self):
        last_state = None
        current_state = None
        same_state_counter = 0
        time_of_next_check = datetime.now() - timedelta(seconds=1)
        
        while True:
            if not self.running or datetime.now() < time_of_next_check:
                time.sleep(1)
                continue
            
            time_of_next_check = datetime.now() + timedelta(seconds=self.waitingtime_ph)
            
            control_logger.info("Checking PH...")
            try:
                with db_handler() as db:
                    min_value, max_value = db.get_range("ph")
                    sensor_data = db.get_sensor_data_most_recent("ph")

                    if sensor_data:
                        current_value = sensor_data[0]["ph_value"]
                        current_state = self.compare_with_range(current_value, min_value, max_value, "ph")

                        #################################################
                        # REGULATION LOGIC
                        #################################################
                        match current_state:
                            case "too low":
                                control_logger.warning("PH too low - adding soda water");
                                same_state_counter += 1
                                if same_state_counter < 5:
                                    self.add_water()
                                else:
                                    self.log_critical_state("ph", current_state)
                            case "too high":
                                control_logger.warning("PH too high - adding citric acid");
                                same_state_counter += 1
                                if same_state_counter < 5:
                                    self.add_low_ph()
                                else:
                                    self.log_critical_state("ph", current_state)
                            case "just right":
                                same_state_counter = 0
                            case _:
                                control_logger.error("something went wrong while comparing ph value to range")
                                
                                
                        #################################################
                        # LAST STATE VS CURRENT STATE
                        #################################################
                        if last_state != current_state:
                            same_state_counter = 0
                            self.log_changed_state("ph", last_state, current_state)
                            
                        last_state = current_state
            except Exception as e:
                control_logger.error("something went wrong while regulating ph: " + str(e))
                
    def regulate_light(self):
        time_of_next_check = datetime.now() - timedelta(seconds=1)
        
        while True:
            if not self.running or datetime.now() < time_of_next_check:
                time.sleep(1)
                continue
            
            time_of_next_check = datetime.now() + timedelta(seconds=self.waitingtime_light)
            
            control_logger.info("Checking Light...")
            try:
                with db_handler() as db:
                    start_time, end_time = db.get_range("light")
                    current_time = datetime.now()
                    
                    if start_time <= current_time and current_time <= end_time:
                        control_logger.info("It's time to turn on the light - turning on light")
                        self.light_on()
                    else:
                        control_logger.info("It's time to turn off the light - turning off light")
                        self.light_off()
            except Exception as e:
                control_logger.error("something went wrong while regulating light: " + str(e))


    def regulate_waterlevel(self):
        empty_water_counter = 0
        time_of_next_check = datetime.now() - timedelta(seconds=1)
        
        while True:
            if not self.running or datetime.now() < time_of_next_check:
                time.sleep(1)
                continue
            
            time_of_next_check = datetime.now() + timedelta(seconds=self.waitingtime_water)
            
            control_logger.info("Checking Waterlevel...")
            try:
                with db_handler() as db:
                    sensor_data = db.get_sensor_data_most_recent("waterlevel")

                    if sensor_data:
                        current_value = sensor_data[0]["waterlevel_value"]
                        
                        if current_value == 1:
                            control_logger.warning("Waterlevel too low - adding water");
                            empty_water_counter += 1
                            self.add_water()
                        else:
                            empty_water_counter = 0
                        
                        if empty_water_counter >= 5:
                            self.log_critical_state("waterlevel", "too low")
            except Exception as e:
                control_logger.error("something went wrong while regulating waterlevel: " + str(e))
        
    def compare_with_range(self, current_value, min_value, max_value, s=None):
        control_logger.info("Comparing <" + str(current_value) + "> value to range <" + str(min_value) + ", " + str(max_value) + ">")
        if current_value < min_value:
            return "too low"
        elif current_value > max_value:
            return "too high"
        elif min_value <= current_value and current_value <= max_value:
            return "just right"
        else:
            return "fail"

