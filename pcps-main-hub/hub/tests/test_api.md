# SmartGarden API Testing with Postman

## Introduction

This document outlines the extensive testing performed on the SmartGarden RESTful API using Postman. Postman is a popular API testing tool that allows developers to design, test, and document APIs quickly and efficiently.

## Test Scenarios

### 1. Authentication

#### 1.1 Successful Authentication

- **Scenario 1**: Authenticate the SmartGarden Web-App with the Hub server.
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with valid 'client-device' credentials.
    2. Capture the generated API key.
  - **Expected Result**: Receive a success response with a valid API key.

- **Scenario 2**: Authenticate a Sensor Device with the Hub server.
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with valid 'sensor-device' credentials.
    2. Capture the generated API key.
  - **Expected Result**: Receive a success response with a valid API key.

- **Scenario 3**: Authenticate an Actuator Device with the Hub server.
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with valid 'actuator-device' credentials.
    2. Capture the generated API key.
  - **Expected Result**: Receive a success response with a valid API key.



#### 1.2 Unauthorized Access

- **Scenario 1**: Attempt to authenticate with an unknown device type.
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with an unknown 'unknown-device' as the device type.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating an unrecognized device type.

- **Scenario 2**: Attempt to register a sensor device without specifying supported sensors.
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with 'sensor-device' credentials but without providing a 'sensors' list.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating a missing or empty list of supported sensors.

- **Scenario 3**: Attempt to register an actuator device without specifying supported actuators.
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with 'actuator-device' credentials but without providing an 'actuators' list.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating a missing or empty list of supported actuators.

- **Scenario 4**: Attempt to authenticate with an some form of incorrect credentials (typo, etc.)
  - **Steps**:
    1. Send a POST request to `/api/authenticate` with incorrect or incomplete device credentials.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating unsuccessful authentication.

### 2. Sensors

#### 2.1 Retrieve List of Sensors

- **Scenario 1**: Retrieve the list of supported sensors as a Web-App.
  - **Steps**:
    1. Send a GET request to `/api/sensors/`.
    2. Include the API key in the request headers.
  - **Expected Result**: Recieve a success response with a list of sensors applicable to the Web-App.

- **Scenario 2**: Retrieve the list of supported sensors as a Sensor Device/ Actuator Device.
  - **Steps**:
    1. Send a GET request to `/api/sensors/` as a Sensor Device.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Forbidden response, indicating that retrieving the list of sensors is not allowed for a Sensor Device.

- **Scenario 3**: Retrieve the list of supported sensors without proper authentication.
  - **Steps**:
    1. Send a GET request to `/api/sensors/` without including the API key in the headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that proper authentication is required.

- **Scenario 4**: Attempt to retrieve the list of supported sensors with an incorrect API key.
  - **Steps**:
    1. Send a GET request to `/api/sensors/` with an incorrect or expired API key.
    2. Include the incorrect API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 5**: Attempt to retrieve the list of supported sensors with some form of incorrect credentials/parameters (typo, extra query, etc.)
  - **Steps**:
    1. Send a GET request to `/api/sensors/` with invalid or unexpected parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating an issue with the request parameters.


#### 2.2 Retrieve Sensor Data

**Important Note**: Before running the scenarios for retrieving sensor data the sensor simulators have to be running. These simulators are responsible for generating mock sensor data, and without them, the database won't have the necessary information to fulfill the retrieval requests (or rather would alywas return _null_ as nothing is in the database).

- **Scenario 1**: Retrieve sensor data for a specific sensor with valid parameters.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with valid parameters (start, end, max_entries).
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with the requested sensor data.

- **Scenario 2**: Attempt to retrieve sensor data without proper authentication.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` without including the API key in the headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that proper authentication is required.

- **Scenario 3**: Attempt to retrieve sensor data with an incorrect API key.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with an incorrect or expired API key.
    2. Include the incorrect API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 4**: Attempt to retrieve sensor data as an unautohrized device type (anything else than as the Web-App).
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with as an incorrect device type.
    2. Include the a valid API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 5**: Retrieve sensor data with unexpected optional parameters.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with unexpected optional parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 200 response, indicating success. The hub should be able to ignore any undefined optional parameters.

- **Scenario 6**: Attempt to retrieve data for a non-existent sensor.
  - **Steps**:
    1. Send a GET request to `/api/sensors/nonexistent_sensor` with valid parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Not Found response, indicating that the requested sensor does not exist.

- **Scenario 7**: Retrieve sensor data with only the 'start' parameter.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with only the 'start' parameter.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with sensor data starting from the specified timestamp.

- **Scenario 8**: Retrieve sensor data with only the 'end' parameter.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with only the 'end' parameter.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with sensor data up to the specified timestamp.

- **Scenario 9**: Retrieve sensor data with both 'start' and 'end' parameters.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with both 'start' and 'end' parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with sensor data within the specified time range.

- **Scenario 10**: Retrieve sensor data with 'max_entries' parameter limiting the number of entries.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with the 'max_entries' parameter.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with a maximum number of entries as specified.

- **Scenario 11**: Retrieve sensor data with a combination of 'start', 'end', and 'max_entries' parameters.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with a combination of 'start', 'end', and 'max_entries'.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with sensor data within the specified time range and limited entries.

- **Scenario 12**: Retrieve sensor data with no optional parameters sepcified
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with no optional parameters specified.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with the latest entry.

- **Scenario 13**: Attempt to retrieve sensor data with 'max_entries' exceeding available entries.
  - **Steps**:
    1. Send a GET request to `/api/sensors/<sensor_name>` with 'max_entries' set to a large number.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with all available entries.

#### 2.3 Post Sensor Data

- **Scenario 1**: Send valid sensor data for an existing sensor.
  - **Steps**:
    1. Send a POST request to `/api/sensors/<sensor_name>` with valid sensor data.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response.

- **Scenario 2**: Attempt to post sensor data as an unauthorized device (anything else then a sensor device).
  - **Steps**:
    1. Send a POST request to `/api/sensors/<sensor_type>.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized Request response, indicating wrong device type.

- **Scenario 3**: Attempt to post sensor data without proper authentication.
  - **Steps**:
    1. Send a POST request to `/api/sensors/<sensor_name>` without including the API key in the headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that proper authentication is required.

- **Scenario 4**: Attempt to post sensor data with an incorrect API key.
  - **Steps**:
    1. Send a POST request to `/api/sensors/<sensor_name>` with an incorrect or expired API key.
    2. Include the incorrect API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 5**: Attempt to post sensor data with invalid request payload.
  - **Steps**:
    1. Send a POST request to `/api/sensors/<sensor_name>` with an invalid or incomplete request payload.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating an issue with the request payload.

- **Scenario 6**: Attempt to post sensor data for a non-existent sensor.
  - **Steps**:
    1. Send a POST request to `/api/sensors/nonexistent_sensor` with valid sensor data.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Not Found response, indicating that the specified sensor does not exist.

- **Scenario 7**: Send sensor data with unexpected or additional parameters.
  - **Steps**:
    1. Send a POST request to `/api/sensors/<sensor_name>` with unexpected or additional parameters in the request.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response, ignoring the unexpected parameters.

### 3. Actuators

#### 3.1 Retrieve List of Actuators

- **Scenario 1**: Retrieve the list of supported actuators as a Web-App.
  - **Steps**:
    1. Send a GET request to `/api/actuators/`.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with a list of actuators applicable to the Web-App.

- **Scenario 2**: Retrieve the list of supported actuators as a Sensor Device/Actuator Device.
  - **Steps**:
    1. Send a GET request to `/api/actuators/` as a Sensor Device or Actuator Device.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Forbidden response, indicating that retrieving the list of actuators is not allowed for a Sensor or Actuator Device.

- **Scenario 3**: Retrieve the list of supported actuators without proper authentication.
  - **Steps**:
    1. Send a GET request to `/api/actuators/` without including the API key in the headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that proper authentication is required.

- **Scenario 4**: Attempt to retrieve the list of supported actuators with an incorrect API key.
  - **Steps**:
    1. Send a GET request to `/api/actuators/` with an incorrect or expired API key.
    2. Include the incorrect API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 5**: Attempt to retrieve the list of supported actuators with some form of incorrect credentials/parameters (typo, extra query, etc.).
  - **Steps**:
    1. Send a GET request to `/api/actuators/` with invalid or unexpected parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating an issue with the request parameters.


#### 3.2 Retrieve Actuator Status

- **Scenario 1**: Retrieve the status of a specific actuator as a Web-App.
  - **Steps**:
    1. Send a GET request to `/api/actuators/<actuator_name>`.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response with the current status of the specified actuator.

- **Scenario 2**: Retrieve the status of a specific actuator as a Sensor Device/Actuator Device.
  - **Steps**:
    1. Send a GET request to `/api/actuators/<actuator_name>` as a Sensor Device or Actuator Device.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Forbidden response, indicating that retrieving the status of actuators is not allowed for a Sensor or Actuator Device.

- **Scenario 3**: Retrieve the status of a specific actuator without proper authentication.
  - **Steps**:
    1. Send a GET request to `/api/actuators/<actuator_name>` without including the API key in the headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that proper authentication is required.

- **Scenario 4**: Attempt to retrieve the status of a specific actuator with an incorrect API key.
  - **Steps**:
    1. Send a GET request to `/api/actuators/<actuator_name>` with an incorrect or expired API key.
    2. Include the incorrect API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 5**: Attempt to retrieve the status of a non-existent actuator.
  - **Steps**:
    1. Send a GET request to `/api/actuators/nonexistent_actuator`.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Not Found response, indicating that the specified actuator does not exist.

- **Scenario 6**: Attempt to retrieve the status of an actuator with some form of incorrect credentials/parameters (typo, extra query, etc.).
  - **Steps**:
    1. Send a GET request to `/api/actuators/<actuator_name>` with invalid or unexpected parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating an issue with the request parameters.


#### 3.3 Toggle Actuator

- **Scenario 1**: Toggle the status of a specific actuator to 'on' as a Web-App.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with the 'toggle' parameter set to 'on'.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response indicating the successful toggle of the actuator to 'on'.

- **Scenario 2**: Toggle the status of a specific actuator to 'off' as a Web-App.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with the 'toggle' parameter set to 'off'.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response indicating the successful toggle of the actuator to 'off'.

- **Scenario 3**: Toggle the status of a specific actuator to 'on' as a Sensor Device/Actuator Device.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with the 'toggle' parameter set to 'on' as a Sensor Device or Actuator Device.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Forbidden response, indicating that toggling the status of actuators is not allowed for a Sensor or Actuator Device.

- **Scenario 4**: Toggle the status of a specific actuator to 'off' as a Sensor Device/Actuator Device.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with the 'toggle' parameter set to 'off' as a Sensor Device or Actuator Device.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Forbidden response, indicating that toggling the status of actuators is not allowed for a Sensor or Actuator Device.

- **Scenario 5**: Toggle the status of a specific actuator without proper authentication.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with the 'toggle' parameter without including the API key in the headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that proper authentication is required.

- **Scenario 6**: Attempt to toggle the status of a specific actuator with an incorrect API key.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with the 'toggle' parameter and an incorrect or expired API key.
    2. Include the incorrect API key in the request headers.
  - **Expected Result**: Receive a 400-499 Unauthorized response, indicating that the provided API key is invalid.

- **Scenario 7**: Attempt to toggle the status of a non-existent actuator.
  - **Steps**:
    1. Send a POST request to `/api/actuators/nonexistent_actuator` with the 'toggle' parameter.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Not Found response, indicating that the specified actuator does not exist.

- **Scenario 8**: Attempt to toggle the status of an actuator with some form of incorrect credentials/parameters (typo, extra query, etc.).
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with invalid or unexpected parameters.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a 400-499 Bad Request response, indicating an issue with the request parameters.

- **Scenario 9**: Toggle the status of a specific actuator with unexpected or additional parameters.
  - **Steps**:
    1. Send a POST request to `/api/actuators/<actuator_name>` with unexpected or additional parameters in the request.
    2. Include the API key in the request headers.
  - **Expected Result**: Receive a success response, ignoring the unexpected parameters.


## Conclusion

The SmartGarden API was thoroughly tested using Postman, covering authentication, sensor operations, and actuator operations. All test scenarios were executed successfully, ensuring the reliability and functionality of the API.
