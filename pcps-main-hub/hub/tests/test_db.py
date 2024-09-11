import unittest

from database.database_setup import db_handler

# call with "python3 -m unittest discover tests" from hub directory
class TestDatabaseHandler(unittest.TestCase):            
    def test_add_client_device(self):
        with db_handler(reset_database=True) as db:
            # try to add client device with api key of wrong type
            with self.assertRaises(TypeError):
                db.add_client_device(7389183010, "A4:CF:12:34:56:78", "127.0.0.1")
                assert False
            
            # try to add client device with mac address of wrong type
            with self.assertRaises(TypeError):
                db.add_client_device("7389183010", 123456789, "127.0.0.1")
                assert False
            
            # try to add client device with ip address of wrong type
            with self.assertRaises(TypeError):
                db.add_client_device("7389183010", "A4:CF:12:34:56:78", 127.0)
                assert False
            
            # try to add client device with invalid mac address
            with self.assertRaises(ValueError):
                db.add_client_device("7389183010", "A4:CF:12:34:56:7", "127.0.0.1")
                assert False
            with self.assertRaises(ValueError):
                db.add_client_device("7389183010", "A4:CG:12:34:56:78", "127.0.0.1")
                assert False
            with self.assertRaises(ValueError):
                db.add_client_device("7389183010", "A4:CF:12:34:56", "127.0.0.1")
                assert False
            
            # add correct client device
            db.add_client_device("7389183010", "A4:CF:12:34:56:78", "127.0.0.1")
            
            # check if client device was added correctly
            result = db.execute_query("SELECT * FROM SmartGarden.device")
            assert len(result) == 1
            assert result[0][0] == "A4:CF:12:34:56:78"
            assert result[0][1] == "client-device"
            assert result[0][2] == "7389183010"
            assert result[0][3] == "127.0.0.1"
            
            # try to add client device with same api key
            with self.assertRaises(ValueError):
                db.add_client_device("7389183010", "A4:CF:12:A4:CF:12", "127.0.0.1")
                assert False
            
            with self.assertRaises(ValueError):
                db.add_client_device("0", "A4:CF:12:34:56:78", "127.0.0.1")
                assert False
            
    def test_add_sensor_device(self):
        with db_handler(reset_database=True) as db:
            # try to add sensor device with api key of wrong type
            with self.assertRaises(TypeError):
                db.add_sensor_device(7389183010, "A4:CF:12:34:56:78", "127.0.0.1", ["temperature"])
            
            # try to add sensor device with mac address of wrong type
            with self.assertRaises(TypeError):
                db.add_sensor_device("7389183010", 123456789, "127.0.0.1", ["temperature"])
                assert False
            
            # try to add sensor device with ip address of wrong type
            with self.assertRaises(TypeError):
                db.add_sensor_device("7389183010", "A4:CF:12:34:56:78", 127.0, ["temperature"])
                assert False
            
            # try to add sensor device with empty list of sensor types
            with self.assertRaises(ValueError):
                db.add_sensor_device("7389183010", "A4:CF:12:34:56:78", "127.0.0.1", [])
                assert False
            
            # try to add sensor device with empty list of invalid sensor types
            with self.assertRaises(ValueError):
                db.add_sensor_device("7389183010", "A4:CF:12:34:56:78", "127.0.0.1", ["invalid"])
            
            # try to add sensor device with invalid mac address
            with self.assertRaises(ValueError):
                db.add_sensor_device("7389183010", "A4:CF:12:34:56:7", "127.0.0.1", ["temperature"])
                assert False
            
            with self.assertRaises(ValueError):
                db.add_sensor_device("7389183010", "A4:CF:1K:34:56:7", "127.0.0.1", ["temperature"])
                assert False
            
            with self.assertRaises(ValueError):
                db.add_sensor_device("7389183010", "A4:CF:12:34:56", "127.0.0.1", ["temperature"])
                assert False
            
            # add correct sensor device
            db.add_sensor_device("7389183010", "A4:CF:12:34:56:78", "127.0.0.1", ["temperature"])
            
            # check if sensor device was added correctly
            result = db.execute_query("SELECT * FROM SmartGarden.device")
            assert len(result) == 1
            assert result[0][0] == "A4:CF:12:34:56:78"
            assert result[0][1] == "sensor-device"
            assert result[0][2] == "7389183010"
            assert result[0][3] == "127.0.0.1"
            
            # check if sensor types were added correctly
            result = db.execute_query("SELECT * FROM SmartGarden.sensor")
            assert len(result) == 1
            assert result[0][0] == 1
            assert result[0][1] == "temperature"
            
            # try to add sensor device with same api key
            with self.assertRaises(ValueError):
                db.add_sensor_device("7389183010", "A4:CF:12:A4:CF:12", "127.0.0.1", ["temperature"])
            
            # try to add sensor device with same mac address
            with self.assertRaises(ValueError):
                db.add_sensor_device("0", "A4:CF:12:34:56:78", "127.0.0.1", ["temperature"])
                
            # add another sensor device with same sensor type
            db.add_sensor_device("0", "A4:CF:12:34:56:79", "127.0.0.1", ["temperature"])
            
            # check if sensor types were added correctly
            result = db.execute_query("SELECT * FROM SmartGarden.device")
            assert len(result) == 2
            assert result[1][0] == "A4:CF:12:34:56:79"
            assert result[1][1] == "sensor-device"
            assert result[1][2] == "0"
            assert result[1][3] == "127.0.0.1"
            
            # check if sensor types were added correctly
            result = db.execute_query("SELECT * FROM SmartGarden.sensor")
            assert len(result) == 2
            assert result[1][0] == 2
            assert result[1][1] == "temperature"
            
            