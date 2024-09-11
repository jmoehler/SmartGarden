import mysql.connector
import logging
import datetime
from contextlib import contextmanager
import re

# configure logging
db_logger = logging.getLogger('DATABASE')
db_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
db_logger.addHandler(sh)

class UserExistsException(Exception):
    pass

class EmailExistsException(Exception):
    pass


class DatabaseHandler:
    def __init__(self, reset_database = False, database_name = "SmartGarden"):   
            
        # connect to mysql server
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root"
            )
            db_logger.debug("Connected to database!")
        except:
            db_logger.error("Error: Could not connect to database with <{}@{}>".format("root", "localhost"))
            db_logger.error("Make sure mysql server is running and password <{}> is correct.".format("root"))
            db_logger.error("To change password of a user, log in and change it with:")
            db_logger.error("ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';")
            exit(1)

        # database name
        self.db_name = database_name
        
        # default ranges for sensors
        self.default_ranges = {
            "light": (datetime.time(8,0,0), datetime.time(20,0,0)),
            "temp": (18,22),
            "hum": (40,80),
            "ph": (6.5,7.5),
            "ec": (0.5,1.5)
        }
        
        # for testing purposes, drop database and reinitialize it
        if reset_database:
            self.drop_database()
        self.create_database()
        self.init_database()
            
    ##########################################################
    # DATABASE SETUP
    ##########################################################
    
    def drop_database(self):
        with self.mydb.cursor() as cursor:
            cursor.execute("DROP DATABASE IF EXISTS {}".format(self.db_name))
            self.mydb.commit()
        db_logger.debug("Database dropped/reset!")
       
    def create_database(self):
        with self.mydb.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(self.db_name))
            self.mydb.commit()  
        db_logger.debug("Database created!")
        
    def init_database(self):
        with self.mydb.cursor() as cursor:
            # create a picture analysis table
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.picture_analysis (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                time_of_analysis DATETIME,
                                picture_path VARCHAR(255),
                                result VARCHAR(255),
                                probability FLOAT,
                                recommended_action VARCHAR(255)
                                )""")
            db_logger.debug("picture_analysis table created!")

            # create ranges table
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.ranges (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                template_name VARCHAR(255),
                                active BOOLEAN,
                                light_on TIME,
                                light_off TIME,
                                temp_min INT,
                                temp_max INT,
                                hum_min INT,
                                hum_max INT,
                                ph_min FLOAT,
                                ph_max FLOAT,
                                ec_min FLOAT,
                                ec_max FLOAT
                            )
                            """)
            db_logger.debug("ranges table created!")
            # create log table 
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.log (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                time_of_log DATETIME,
                                status_code INT,
                                sensor_type VARCHAR(255)
                                )""")
            db_logger.debug("log table created!")
            # create login table
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.users (
                                ID INT AUTO_INCREMENT PRIMARY KEY,
                                username VARCHAR(255),
                                email VARCHAR(255), 
                                join_date DATETIME,
                                password VARCHAR(255)
                                )""")
            db_logger.debug("users table created!")
            # create devices table
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.device (
                                id VARCHAR(255) NOT NULL PRIMARY KEY,
                                type VARCHAR(255), 
                                api_key VARCHAR(255),
                                ip_address VARCHAR(255),
                                time_of_first_connection DATETIME,
                                time_of_last_connection DATETIME
                                )""")
            db_logger.debug("device table created!")
            # create sensors table
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.sensor (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                type VARCHAR(255),
                                time_of_last_data DATETIME,
                                device_id VARCHAR(255),
                                FOREIGN KEY (device_id) REFERENCES device(id)
                                )""")
            db_logger.debug("sensor table created!")
            # create a actuator table
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.actuator (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                type VARCHAR(255),
                                time_of_last_trigger DATETIME,
                                device_id VARCHAR(255),
                                FOREIGN KEY (device_id) REFERENCES device(id)
                                )""")
            db_logger.debug("actuator table created!")
            # sensor data tables
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.ph_data (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                ph_value FLOAT,
                                time_of_measurement DATETIME,
                                sensor_id INT,
                                FOREIGN KEY (sensor_id) REFERENCES sensor(id)
                                )""")
            db_logger.debug("ph_data table created!")
            
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.ec_data (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                ec_value FLOAT,
                                time_of_measurement DATETIME,
                                sensor_id INT,
                                FOREIGN KEY (sensor_id) REFERENCES sensor(id)
                                )""")
            db_logger.debug("ec_data table created!")
            
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.temperature_data (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                temperature_value FLOAT,
                                time_of_measurement DATETIME,
                                sensor_id INT,
                                FOREIGN KEY (sensor_id) REFERENCES sensor(id)
                                )""")
            db_logger.debug("temperature_data table created!")
            
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.humidity_data (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                humidity_value FLOAT,
                                time_of_measurement DATETIME,
                                sensor_id INT,
                                FOREIGN KEY (sensor_id) REFERENCES sensor(id)
                                )""")
            db_logger.debug("humidity_data table created!")

            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.waterlevel_data (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                waterlevel_value FLOAT,
                                time_of_measurement DATETIME,
                                sensor_id INT,
                                FOREIGN KEY (sensor_id) REFERENCES sensor(id)
                                )""")
            db_logger.debug("waterlevel_data table created!")
            
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.db_name}.light_data (
                                id INT PRIMARY KEY AUTO_INCREMENT,
                                visible_value FLOAT,
                                ir_value FLOAT,
                                uv_value FLOAT,
                                time_of_measurement DATETIME,
                                sensor_id INT,
                                FOREIGN KEY (sensor_id) REFERENCES sensor(id)
                                )""")
            db_logger.debug("light_data table created!")
            
            # commit changes
            self.mydb.commit()
        
            db_logger.debug("Database initialized!")
    
    ##########################################################
    # USER MANAGEMENT
    ##########################################################
    
    def add_user(self, username, email, password): 
        if not isinstance(username, str) or not isinstance(email, str) or not isinstance(password, str):
            raise TypeError("Non-string input: <{}>, <{}>, <{}>".format(username, email, password))
        
        with self.mydb.cursor() as cursor:
            # check if username already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.users WHERE username = '{username}'")
            user = cursor.fetchone()
            
            if user:
                raise UserExistsException()
            
            # check if email already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.users WHERE email = '{email}'")
            email = cursor.fetchone()
            
            if email:
                raise EmailExistsException()
            
            cursor.execute(f"""INSERT INTO {self.db_name}.users (username, email, join_date, password) 
                                    VALUES ('{username}', '{email}', NOW(), '{password}')""")
            self.mydb.commit()
            
            db_logger.debug(f"User <{username}> [<{email}>] with <{password}> added to database")
                
    def get_password(self, username):
        if not isinstance(username, str):
            raise TypeError("Non-string input: <{}>".format(username))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT password FROM {self.db_name}.users WHERE username = '{username}'")
            password = cursor.fetchone()
            
            if password:
                return password[0]
            else:
                return None
         
    def user_exists(self, username):
        if not isinstance(username, str):
            raise TypeError("Non-string input: <{}>".format(username))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.db_name}.users WHERE username = '{username}'")
            user = cursor.fetchone()
            
            if user:
                return True
            else:
                return False


    ##########################################################
    # PICTURE ANALYSIS
    ##########################################################

    def add_picture_analysis(self, picture_path, result, probability, recommended_action):
            if not isinstance(picture_path, str) or not isinstance(result, str) or not isinstance(recommended_action, str):
                raise TypeError("Non-string input: <{}>, <{}>, <{}>, <{}>".format(picture_path, result, recommended_action))
            
            with self.mydb.cursor() as cursor:
                cursor.execute(f"""INSERT INTO {self.db_name}.picture_analysis (time_of_analysis, picture_path, result, probability, recommended_action) 
                                        VALUES (NOW(), '{picture_path}', '{result}', '{probability}', '{recommended_action}')""")
                self.mydb.commit()
                
                db_logger.debug("Picture analysis added to database")

    


    def get_most_recent_picture_analysis(self):
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT picture_path, result, probability, recommended_action FROM {self.db_name}.picture_analysis ORDER BY time_of_analysis DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                return {"picture_path": result[0], "result": result[1], "probability": result[2], "recommended_action": result[3]}
            else:
                return None


 
            
    def get_all_picture_analysis(self):
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT picture_path, result, probability, recommended_action FROM {self.db_name}.picture_analysis")
            results = cursor.fetchall()
            
            if results:
                return list(map(lambda x: {"picture_path": x[0], "result": x[1], "probability": x[2], "recomended_action": x[2]}, results))
            else:
                return []

    
    ##########################################################  
    # LOGGING
    ##########################################################
    
    def add_log(self, status_code, sensor_type):
        if not isinstance(status_code, int):
            raise TypeError("Non-integer input: <{}>".format(status_code))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"""INSERT INTO {self.db_name}.log (time_of_log, status_code, sensor_type) 
                                    VALUES (NOW(), {status_code}, '{sensor_type}')""")
            self.mydb.commit()
            
        db_logger.debug("Log with status code <{}> added to database".format(status_code))
            
    def get_all_logs(self):
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT time_of_log, status_code FROM {self.db_name}.log")
            logs = cursor.fetchall()
            if logs:
                logs = list(map(lambda x: {"timestamp": x[0], "statuscode": x[1]}, logs))
        
            return logs
        
    def get_logs(self, limit = 10, offset = 0, sensor_type = None):
        with self.mydb.cursor() as cursor:
            if not sensor_type:
                sensor_type = "'water', 'temperature', 'light'"
            cursor.execute(f"""SELECT DATE_FORMAT(time_of_log, '%Y-%m-%d %H:%i:%s') AS formatted_date, status_code, sensor_type 
                               FROM {self.db_name}.log 
                               WHERE sensor_type IN ({sensor_type})
                               ORDER BY time_of_log DESC
                               LIMIT {offset}, {limit}""")
            logs = cursor.fetchall()
            if logs:
                logs = list(map(lambda x: {"timestamp": x[0], "statuscode": x[1], "sensor_type": x[2]}, logs))
        
            return logs
    
    def delete_all_logs(self):
        with self.mydb.cursor() as cursor:
            cursor.execute(f"DELETE FROM {self.db_name}.log")
        
        self.mydb.commit()

    ##########################################################
    # RANGE TEMPLATES
    ##########################################################   
    def add_ranges(self, template_name, light_on = None, light_off = None, temp_min = None, temp_max = None, hum_min = None, hum_max = None, ph_min = None, ph_max = None, ec_min = None, ec_max = None):
        if not isinstance(template_name, str):
            raise TypeError("Non-string input: <{}>".format(template_name))
        
        if light_on and not isinstance(light_on, datetime.time) or light_off and not isinstance(light_off, datetime.time):
            raise TypeError("Non-time input: <{}>, <{}>".format(light_on, light_off))
        
        if temp_min and not isinstance(temp_min, int) or temp_max and not isinstance(temp_max, int):
            raise TypeError("Non-integer input: <{}>, <{}>".format(temp_min, temp_max))
        
        if hum_min and not isinstance(hum_min, int) or hum_max and not isinstance(hum_max, int):
            raise TypeError("Non-integer input: <{}>, <{}>".format(hum_min, hum_max))
        
        if ph_min and not isinstance(ph_min, float) or ph_max and not isinstance(ph_max, float):
            raise TypeError("Non-float input: <{}>, <{}>".format(ph_min, ph_max))
        
        if ec_min and not isinstance(ec_min, float) or ec_max and not isinstance(ec_max, float):
            raise TypeError("Non-float input: <{}>, <{}>".format(ec_min, ec_max))    
        
        with self.mydb.cursor() as cursor:
            # check if template already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.ranges WHERE template_name = '{template_name}'")
            template = cursor.fetchone()
            
            if template:
                raise ValueError("Template already exists")
            
            # NOTE: COALESCE() uses the first non-null value
            # set the first template active, else it is set to unactive until user sets it to active.
            if (self.ranges_is_empty()):
                insert_query = f"""INSERT INTO {self.db_name}.ranges (template_name, active, light_on, light_off, temp_min, temp_max, hum_min, hum_max, ph_min, ph_max, ec_min, ec_max)
                                    VALUES (%s, 1, COALESCE(%s, %s), COALESCE(%s, %s), COALESCE(%s, {self.default_ranges["temp"][0]}), COALESCE(%s, {self.default_ranges["temp"][1]}), COALESCE(%s, {self.default_ranges["hum"][0]}), COALESCE(%s, {self.default_ranges["hum"][1]}), COALESCE(%s, {self.default_ranges["ph"][0]}), COALESCE(%s, {self.default_ranges["ph"][1]}), COALESCE(%s, {self.default_ranges["ec"][0]}), COALESCE(%s, {self.default_ranges["ec"][1]}))"""
            else:
                insert_query = f"""INSERT INTO {self.db_name}.ranges (template_name, active, light_on, light_off, temp_min, temp_max, hum_min, hum_max, ph_min, ph_max, ec_min, ec_max)
                                    VALUES (%s, 0, COALESCE(%s, %s), COALESCE(%s, %s), COALESCE(%s, {self.default_ranges["temp"][0]}), COALESCE(%s, {self.default_ranges["temp"][1]}), COALESCE(%s, {self.default_ranges["hum"][0]}), COALESCE(%s, {self.default_ranges["hum"][1]}), COALESCE(%s, {self.default_ranges["ph"][0]}), COALESCE(%s, {self.default_ranges["ph"][1]}), COALESCE(%s, {self.default_ranges["ec"][0]}), COALESCE(%s, {self.default_ranges["ec"][1]}))"""
            
            cursor.execute(insert_query, (template_name, light_on, self.default_ranges["light"][0], light_off, self.default_ranges["light"][1], temp_min, temp_max, hum_min, hum_max, ph_min, ph_max, ec_min, ec_max))
            
            self.mydb.commit()
            
        db_logger.debug("New template <{}> added to database".format(template_name))
    
    def activate_template(self, template_name):
        with self.mydb.cursor() as cursor:
            # Aktiviere die spezifische Vorlage
            activate_query = f"""UPDATE {self.db_name}.ranges
                                SET active = 1
                                WHERE template_name = %s"""
            cursor.execute(activate_query, (template_name,))

            # Deaktiviere alle anderen Vorlagen
            deactivate_query = f"""UPDATE {self.db_name}.ranges
                                SET active = 0
                                WHERE template_name != %s"""
            cursor.execute(deactivate_query, (template_name,))

        self.mydb.commit()

    def get_all_templates(self):
        with self.mydb.cursor() as cursor:
            if self.ranges_is_empty():
                return []

            cursor.execute(f"SELECT * FROM {self.db_name}.ranges")
            templates = cursor.fetchall()
                
            return templates

    def change_active_template(self, template_name):
        if not isinstance(template_name, str):
            raise TypeError("Non-string input: <{}>".format(template_name))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.db_name}.ranges WHERE template_name = '{template_name}'")
            template = cursor.fetchone()

            if not template:
                raise ValueError("Template does not exist")
            
            cursor.execute(f"""UPDATE {self.db_name}.ranges
                                SET active = 0
                                WHERE active = 1""")
            cursor.execute(f"""UPDATE {self.db_name}.ranges
                                SET active = 1
                                WHERE template_name = '{template_name}'""")
            self.mydb.commit()
        
        db_logger.debug("Active template changed to <{}>".format(template_name))
    
    def get_range(self, value_type):
        if value_type not in ["light", "temp", "hum", "ph", "ec"]:
            raise ValueError("Invalid value type")
        
        with self.mydb.cursor() as cursor:
            if value_type == "light":
                cursor.execute(f"SELECT {value_type}_on, {value_type}_off FROM {self.db_name}.ranges WHERE active = 1")
                result = cursor.fetchone()
                
                if result:
                    # convert time to datetime
                    # example: 00:00:00 -> 2021-05-01 00:00:00 (if today is 2021-05-01)
                    today = datetime.datetime.today()
                    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    return (today + result[0], today + result[1])
                else:
                    return (datetime.datetime.combine(datetime.date.today(), self.default_ranges[value_type][0]), datetime.datetime.combine(datetime.date.today(), self.default_ranges[value_type][1]))
            else:
                cursor.execute(f"SELECT {value_type}_min, {value_type}_max FROM {self.db_name}.ranges WHERE active = 1")
                result = cursor.fetchone()
            
                if result:
                    return result
                else:
                    return self.default_ranges[value_type]
                  
    def get_active_template_name(self):
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT template_name FROM {self.db_name}.ranges WHERE active = 1")
            result = cursor.fetchone() 
            
            if not result:
                return None
            
            return result[0]
        
    def ranges_is_empty(self):
       with self.mydb.cursor() as cursor:
           cursor.execute(f"SELECT * FROM {self.db_name}.ranges LIMIT 1")
           result = cursor.fetchall()
           if result:
                return False
           return True
            
    def update_active_ranges(self, template_name=None, light_on = None, light_off = None, temp_min = None, temp_max = None, hum_min = None, hum_max = None, ph_min = None, ph_max = None, ec_min = None, ec_max = None):
        if light_on and not isinstance(light_on, datetime.time) or light_off and not isinstance(light_off, datetime.time):
            raise TypeError("Non-time input: <{}>, <{}>".format(light_on, light_off))
        
        if temp_min and not isinstance(temp_min, int) or temp_max and not isinstance(temp_max, int):
            raise TypeError("Non-integer input: <{}>, <{}>".format(temp_min, temp_max))
        
        if hum_min and not isinstance(hum_min, int) or hum_max and not isinstance(hum_max, int):
            raise TypeError("Non-integer input: <{}>, <{}>".format(hum_min, hum_max))
        
        if ph_min and not isinstance(ph_min, float) or ph_max and not isinstance(ph_max, float):
            raise TypeError("Non-float input: <{}>, <{}>".format(ph_min, ph_max))
        
        if ec_min and not isinstance(ec_min, float) or ec_max and not isinstance(ec_max, float):
            raise TypeError("Non-float input: <{}>, <{}>".format(ec_min, ec_max))
        
        if template_name and not isinstance(template_name, str):
            raise TypeError("Non-String input: <{}>".format(template_name))
        
        with self.mydb.cursor() as cursor:
            # NOTE: COALESCE() uses the first non-null value
            update_query = f"""UPDATE {self.db_name}.ranges
                                SET light_on = COALESCE(%s, light_on),
                                light_off = COALESCE(%s, light_off),
                                temp_min = COALESCE(%s, temp_min),
                                temp_max = COALESCE(%s, temp_max),
                                hum_min = COALESCE(%s, hum_min),
                                hum_max = COALESCE(%s, hum_max),
                                ph_min = COALESCE(%s, ph_min),
                                ph_max = COALESCE(%s, ph_max),
                                ec_min = COALESCE(%s, ec_min),
                                ec_max = COALESCE(%s, ec_max),
                                template_name = %s
                                WHERE active = 1"""
                                
            cursor.execute(update_query, (light_on, light_off, temp_min, temp_max, hum_min, hum_max, ph_min, ph_max, ec_min, ec_max, template_name))
        
            self.mydb.commit()
            
        db_logger.debug("Ranged of active template updated")
    
    def get_all_template_names(self):
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT template_name FROM {self.db_name}.ranges")
            template_names = cursor.fetchall()
            
            if template_names:
                return [template_name[0] for template_name in template_names]
            else:
                return []  

    def delete_template(self, template_name):
        if not isinstance(template_name, str):
            raise TypeError("Non-string input: <{}>".format(template_name))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"DELETE FROM {self.db_name}.ranges WHERE template_name = '{template_name}'")
            self.mydb.commit()
            
        db_logger.debug("Template <{}> deleted".format(template_name))
    
    def template_active(self, template_name):
        if not isinstance(template_name, str):
            raise TypeError("Non-string input: <{}>".format(template_name))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT active FROM {self.db_name}.ranges WHERE template_name = '{template_name}'")

            result = cursor.fetchone()
            if result == 1:
                return True
            return False

    ##########################################################
    # DEVICE MANAGEMENT
    ##########################################################
    def add_client_device(self, api_key, device_id, ip_address):
        if not isinstance(api_key, str) or not isinstance(ip_address, str) or not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>, <{}>, <{}>".format(api_key, ip_address, device_id))
            raise TypeError("Non-string input: <{}>, <{}>, <{}>".format(api_key, ip_address, device_id))
        
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$" , device_id.lower()) == None:
            db_logger.error("Invalid device_id - has to be a valid mac-address")
            raise ValueError("Invalid device_id - has to be a valid mac-address")
        
        with self.mydb.cursor() as cursor:
            # check if device_id already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE id = '{device_id}'")
            device = cursor.fetchone()
            
            if device:
                db_logger.error("Trying to add device <{}> that already exists".format(device_id))
                raise ValueError("Device already exists")
            
            # check if api_key already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE api_key = '{api_key}'")
            key = cursor.fetchone()
                         
            if key:
                db_logger.error("Trying to add device <{}> with api key <{}> that already exists".format(device_id, api_key))
                raise ValueError("API key already exists")
            
            
            cursor.execute(f"""INSERT INTO {self.db_name}.device (id, type, api_key, ip_address, time_of_first_connection, time_of_last_connection) 
                                    VALUES ('{device_id}', 'client-device', '{api_key}', '{ip_address}',NOW(), NOW())""")
            self.mydb.commit()
            
            db_logger.debug("Client device <{}> added to database".format(device_id))
    
    def add_sensor_device(self, api_key, device_id, ip_address, sensors=[]):
        if not isinstance(api_key, str) or not isinstance(ip_address, str) or not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>, <{}>, <{}>".format(api_key, ip_address, device_id))
            raise TypeError("Non-string input: <{}>, <{}>, <{}>".format(api_key, ip_address, device_id))
        
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$" , device_id.lower()) == None:
            db_logger.error("Invalid device_id - has to be a valid mac-address")
            raise ValueError("Invalid device_id - has to be a valid mac-address")
        
        if sensors == []:
            db_logger.error("No sensors specified")
            raise ValueError("No sensors specified")

        for sensor_type in sensors:
            if sensor_type not in ["ph", "ec", "temperature", "humidity", "waterlevel", "light"]:
                db_logger.error("Invalid sensor type")
                raise ValueError("Invalid sensor type")
    
        with self.mydb.cursor() as cursor:
            # check if device_id already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE id = '{device_id}'")
            device = cursor.fetchone()
            
            if device:
                db_logger.error("Trying to add device <{}> that already exists".format(device_id))
                raise ValueError("Device already exists")
            
            # check if api_key already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE api_key = '{api_key}'")
            key = cursor.fetchone()
                         
            if key:
                db_logger.error("Trying to add device <{}> with api key <{}> that already exists".format(device_id, api_key))
                raise ValueError("API key already exists")
            
            cursor.execute(f"""INSERT INTO {self.db_name}.device (id, type, api_key, ip_address, time_of_first_connection, time_of_last_connection) 
                                    VALUES ('{device_id}', 'sensor-device', '{api_key}','{ip_address}', NOW(), NOW())""")
            self.mydb.commit()
            
            db_logger.debug("Sensor device <{}> added to database".format(device_id))
            
            for sensor_type in sensors:
                cursor.execute(f"""INSERT INTO {self.db_name}.sensor (type, time_of_last_data, device_id)
                                    VALUES ('{sensor_type}', NULL, '{device_id}')""")
                self.mydb.commit()
                
                db_logger.debug("Sensor <{}> added to database".format(sensor_type))
     
    def add_actuator_device(self, api_key, device_id, ip_address, actuators=[]):
        if not isinstance(api_key, str) or not isinstance(ip_address, str) or not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>, <{}>, <{}>".format(api_key, ip_address, device_id))
            raise TypeError("Non-string input: <{}>, <{}>, <{}>".format(api_key, ip_address, device_id))
        
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$" , device_id.lower()) == None:
            db_logger.error("Invalid device_id - has to be a valid mac-address")
            raise ValueError("Invalid device_id - has to be a valid mac-address")
        
        if actuators == []:
            db_logger.error("No actuators specified")
            raise ValueError("No actuators specified")
        
        for actuator_type in actuators:
            if actuator_type not in ["led", "waterpump", "ecpump", "phpump"]:
                db_logger.error("Invalid actuator type")
                raise ValueError("Invalid actuator type")
        
        with self.mydb.cursor() as cursor:
            # check if device_id already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE id = '{device_id}'")
            device = cursor.fetchone()
            
            if device:
                db_logger.error("Trying to add device <{}> that already exists".format(device_id))
                raise ValueError("Device already exists")
            
            # check if api_key already exists
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE api_key = '{api_key}'")
            key = cursor.fetchone()
                         
            if key:
                db_logger.error("Trying to add device <{}> with api key <{}> that already exists".format(device_id, api_key))
                raise ValueError("API key already exists")
            
            cursor.execute(f"""INSERT INTO {self.db_name}.device (id, type, api_key, ip_address, time_of_first_connection, time_of_last_connection) 
                                    VALUES ('{device_id}', 'actuator-device', '{api_key}', '{ip_address}', NOW(), NOW())""")
            self.mydb.commit()
            
            db_logger.debug("Actuator device <{}> added to database".format(device_id))
            
            for actuator_type in actuators:
                cursor.execute(f"""INSERT INTO {self.db_name}.actuator (type, time_of_last_trigger, device_id)
                                    VALUES ('{actuator_type}', NULL, '{device_id}')""")
                self.mydb.commit()
                
                db_logger.debug("Actuator <{}> added to database".format(actuator_type))
    
    def update_ip_address(self, device_id, ip_address):
        if not isinstance(ip_address, str) or not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>, <{}>".format(ip_address, device_id))
            raise TypeError("Non-string input: <{}> <{}>".format(ip_address, device_id))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"""UPDATE {self.db_name}.device
                                SET ip_address = '{ip_address}'
                                WHERE id = '{device_id}'""")
            self.mydb.commit()
            
        db_logger.debug("IP address of device <{}> updated to <{}>".format(device_id, ip_address))
    
    def is_known_device(self, device_id):
        if not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>".format(device_id))
            raise TypeError("Non-string input: <{}>".format(device_id))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE id = '{device_id}'")
            device = cursor.fetchone()
            
            if device:
                return True
            else:
                return False
            
    def get_api_key(self, device_id):
        if not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>".format(device_id))
            raise TypeError("Non-string input: <{}>".format(device_id))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT api_key FROM {self.db_name}.device WHERE id = '{device_id}'")
            api_key = cursor.fetchone()
            
            if api_key:
                return api_key[0]
            else:
                return None

    def update_time_of_last_data(self, device_id, sensor_type):
        if not isinstance(device_id, str) or not isinstance(sensor_type, str):
            db_logger.error("Non-string input: <{}>, <{}>".format(device_id, sensor_type))
            raise TypeError("Non-string input: <{}>, <{}>".format(device_id, sensor_type))
        
        with self.mydb.cursor() as cursor:
            get_sensor_id_query = f"""SELECT id FROM {self.db_name}.sensor WHERE device_id = '{device_id}' AND type = '{sensor_type}'"""
            cursor.execute(get_sensor_id_query)
            sensor_id = cursor.fetchone()
            
            if sensor_id:
                sensor_id = sensor_id[0]
            else:
                db_logger.error("No <{}> sensor found for device <{}>".format(sensor_type, device_id))
                raise Exception("no <{}> sensor found for device <{}>".format(sensor_type, device_id))
            
            cursor.execute(f"""UPDATE {self.db_name}.sensor
                                SET time_of_last_data = NOW()
                                WHERE id = {sensor_id}""")
            self.mydb.commit()
        
        db_logger.debug("Time of last data of sensor <{}> updated".format(sensor_type))
        

    def update_time_of_last_connection(self, device_id):
        if not isinstance(device_id, str):
            db_logger.error("Non-string input: <{}>".format(device_id))
            raise TypeError("Non-string input: <{}>".format(device_id))
        
        with self.mydb.cursor() as cursor:
            # check if there is a device with the given id
            cursor.execute(f"SELECT * FROM {self.db_name}.device WHERE id = '{device_id}'")
            device = cursor.fetchone()
            
            if not device:
                db_logger.error("No device with id <{}> found".format(device_id))
                raise Exception("No device with id <{}> found".format(device_id))
            
            cursor.execute(f"""UPDATE {self.db_name}.device
                                SET time_of_last_connection = NOW()
                                WHERE id = '{device_id}'""")
            self.mydb.commit()
            
        db_logger.debug("Time of last connection of device <{}> updated".format(device_id))


    # check if the api key is valid
    def check_authorization(self, api_key):
        if not isinstance(api_key, str):
            db_logger.error("Non-string input: <{}>".format(api_key))
            raise TypeError("Non-string input: <{}>".format(api_key))
        
        with self.mydb.cursor() as cursor:
            get_device_id_query = f"SELECT id, type FROM {self.db_name}.device WHERE api_key = '{api_key}'"
            cursor.execute(get_device_id_query)
            device = cursor.fetchone()
            
            if device:
                self.update_time_of_last_connection(device[0])
                return (True, device[0], device[1])
            else:
                return (False, None, None)
    
    # given a actuator type, return a list of api-key and api-endpoint tuples 
    def get_actuator_connection_details(self, actuator_type):
        if not isinstance(actuator_type, str):
            db_logger.error("Non-string input: <{}>".format(actuator_type))
            raise TypeError("Non-string input: <{}>".format(actuator_type))
        
        if actuator_type not in ["led", "waterpump", "ecpump", "phpump"]:
            db_logger.error("Invalid actuator type")
            raise ValueError("Invalid actuator type")
        
        with self.mydb.cursor() as cursor:
            # get api key and ip_adress from device table for the given actuator type from the actuator table
            get_device_id_query = f"""SELECT device.api_key, device.ip_address FROM {self.db_name}.device
                                        INNER JOIN {self.db_name}.actuator ON device.id = actuator.device_id
                                        WHERE actuator.type = '{actuator_type}'"""
            cursor.execute(get_device_id_query)
            devices = cursor.fetchall()
            
            if devices:
                return devices
            else:
                raise Exception("No such actuator currently available")
    
    ##########################################################
    # SENSOR DATA
    ##########################################################
    
    def get_sensor_id(self, device_id, sensor_type):
        with self.mydb.cursor() as cursor:
            get_sensor_id_query = f"""SELECT id FROM {self.db_name}.sensor WHERE device_id = '{device_id}' AND type = '{sensor_type}'"""
            cursor.execute(get_sensor_id_query)
            sensor_id = cursor.fetchone()
            
            if sensor_id:
                sensor_id = sensor_id[0]
            else:
                db_logger.error("No <{}> sensor found for device <{}>".format(sensor_type, device_id))
                raise Exception("no <{}> sensor found for device <{}>".format(sensor_type, device_id))
            
            return sensor_id

    def add_sensor_data(self, device_id, sensor_type, data):
        if not isinstance(device_id, str) or not isinstance(sensor_type, str):
            db_logger.error("Non-string input: <{}>, <{}>".format(device_id, sensor_type))
            raise TypeError("Non-string input: <{}>, <{}>".format(device_id, sensor_type))
        
        if not isinstance(data, dict):
            db_logger.error("Non-dict input: <{}>".format(data))
            raise TypeError("Non-dict input: <{}>".format(data))
        
        if sensor_type not in ["ph", "ec", "temperature", "humidity", "waterlevel", "light"]:
            db_logger.error("Invalid sensor type")
            raise ValueError("Invalid sensor type")
        
        with self.mydb.cursor() as cursor:
            get_sensor_id_query = f"""SELECT id FROM {self.db_name}.sensor WHERE device_id = '{device_id}' AND type = '{sensor_type}'"""
            cursor.execute(get_sensor_id_query)
            sensor_id = cursor.fetchone()
            
            if sensor_id:
                sensor_id = sensor_id[0]
            else:
                db_logger.error("No <{}> sensor found for device <{}>".format(sensor_type, device_id))
                raise Exception("no <{}> sensor found for device <{}>".format(sensor_type, device_id))
            
            data_columns_str = ', '.join(f'{value_name}_value' for value_name in data.keys())
            data_values_str = ', '.join(str(value) for value in data.values())
            add_data_query = f"""INSERT INTO {self.db_name}.{sensor_type}_data ({data_columns_str}, time_of_measurement, sensor_id) 
                                    VALUES ({data_values_str}, NOW(), {sensor_id})"""
            
            cursor.execute(add_data_query)
            self.mydb.commit()
            db_logger.debug("Sensor data <{}> added to database".format(data))
            
            self.update_time_of_last_data(device_id, sensor_type)
            self.update_time_of_last_connection(device_id)
        
    def get_sensor_data_most_recent(self, sensor_type):
        if not isinstance(sensor_type, str):
            db_logger.error("Non-string input: <{}>".format(sensor_type))
            raise TypeError("Non-string input: <{}>".format(sensor_type))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {self.db_name}.{sensor_type}_data")
            column_names = map(lambda x: x[0], cursor.fetchall())
            column_names = list(filter(lambda x: x not in ["id", "sensor_id"], column_names))
            column_names_str = ", ".join(column_names)
            
            cursor.execute(f"SELECT {column_names_str} FROM {self.db_name}.{sensor_type}_data ORDER BY time_of_measurement DESC LIMIT 1")
            data = cursor.fetchone()
              
            if data:
                data = dict(zip(column_names, data))
                data["time_of_measurement"] = str(data["time_of_measurement"])
                return [data]
            else:
                return None
    
    def get_sensor_data(self, sensor_type, start, end, max_entries):
        with self.mydb.cursor() as cursor:
            # extract column names of table which are not id or sensor_id
            cursor.execute(f"SHOW COLUMNS FROM {self.db_name}.{sensor_type}_data")
            column_names = map(lambda x: x[0], cursor.fetchall())
            column_names = list(filter(lambda x: x not in ["id", "sensor_id"], column_names))
            column_names_str = ", ".join(column_names)
            
            if not start and not end and not max_entries:
                # if no parameters are provided, get the latest entry
                get_data_query = f"""SELECT
                                    {column_names_str}
                                    FROM
                                    {self.db_name}.{sensor_type}_data
                                    ORDER BY time_of_measurement DESC
                                    LIMIT 1;
                                    """
            else:
                # set default values, if none were provided
                if not start:
                    start = "1900-01-01 00:00:00"
                if not end:
                    end = "2100-01-01 00:00:00"
                if not max_entries:
                    max_entries = 1000
                    
                get_data_query = f"""WITH numbered_data AS (
                                        SELECT
                                            *,
                                            ROW_NUMBER() OVER (ORDER BY time_of_measurement) AS row_num
                                        FROM
                                            {self.db_name}.{sensor_type}_data
                                        WHERE
                                            time_of_measurement >= '{start}'
                                            AND time_of_measurement <= '{end}'
                                        )
                                        SELECT
                                        {column_names_str}
                                        FROM
                                        numbered_data
                                        WHERE
                                        row_num % GREATEST(FLOOR((SELECT COUNT(*) FROM numbered_data) / {max_entries}),1) = 0 
                                        ORDER BY time_of_measurement
                                        LIMIT {max_entries};
                                        """
                                    
            cursor.execute(get_data_query)
            data = cursor.fetchall()
            
            if data:
                # parse the data 
                data = list(map(lambda x: dict(zip(column_names, x)), data))
                for entry in data:
                    entry["time_of_measurement"] = str(entry["time_of_measurement"])
                    
                return data
            else:
                return None
            

    def get_sensor_data_day(self, sensor_type, date):
        if not isinstance(sensor_type, str) or not isinstance(date, str):
            db_logger.error("Non-string input: <{}>, <{}>.".format(sensor_type, date))
            raise TypeError("Non-string input: <{}>, <{}>.".format(sensor_type, date))
        
        with self.mydb.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.db_name}.{sensor_type}_data WHERE DATE(time_of_measurement) = '{date}'")
            data = cursor.fetchall()

            return data

            
    def getHistory(self, sensor_type, column, time_interval):
        with self.mydb.cursor() as cursor: 
            cursor.execute(f""" SELECT ({column}_value)
                                FROM {self.db_name}.{sensor_type}_data
                                WHERE time_of_measurement >= NOW() - INTERVAL {time_interval} SECOND
                                ORDER BY time_of_measurement DESC;""")
            res = cursor.fetchall()
            if res:
                return list(map(lambda x: x[0], res))
            else:
                return None



    ##########################################################
    # PRINTING
    ##########################################################
            
    # pretty print a table
    def print_table(self, table_name):
        try:
            with self.mydb.cursor() as cursor:
                get_table_query = f"SELECT * FROM {self.db_name}.{table_name}"
                cursor.execute(get_table_query)
                results = cursor.fetchall()
                
                if results:
                    # get the column names from the cursor description
                    column_names = [description[0] for description in cursor.description]

                    # calculate the maximum width for each column
                    column_widths = [max(len(name), max(len(str(row[i])) for row in results)) for i, name in enumerate(column_names)]

                    # create the header
                    header = "| " + " | ".join(f"{name:{width}}" for name, width in zip(column_names, column_widths)) + " |"

                    # create a separator line
                    separator = "+-" + "-+-".join("-" * width for width in column_widths) + "-+"

                    # create the table content
                    content = []
                    for row in results:
                        row_str = "| " + " | ".join(f"{str(value):{width}}" for value, width in zip(row, column_widths)) + " |"
                        content.append(row_str)

                    # print the table
                    print(separator)
                    print(header)
                    print(separator)
                    for row_str in content:
                        print(row_str)
                    print(separator)
                else:
                    print("No data found in the table.")

        except Exception as err:
            print(f"Error: {err}")

    def execute_query(self, query):
        with self.mydb.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    
    # closes the connection to the database
    def close(self):
        self.mydb.close()

@contextmanager
def db_handler(reset_database = False, database_name = "SmartGarden"):
    db = DatabaseHandler(reset_database, database_name)
    try:
        yield db
    finally:
        db.close()
        