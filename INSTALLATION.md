# Installition Guide

The Hub is connected to the local WiFi network (planthubwifi) and has all the code such as the webserver, autocontroller, camera and mDNS running. 

## Step 1: Connect to WiFi
- Connect your device (such as a latop) to the WiFi network `planthubwifi` using the password `WdBKADGBDRxefs6`.

## Step 2: Access the Webserver
- Open a web browser and access the webpage using the following URL: `http://192.168.1.133:8000/`

## Step 3: Register a new user
- The hub is set to factory settings, hence you need to register a new user. Click on the `Register` button and fill in the required details to register a new user.

## Step 4: Login
- Once registered, you can login using the credentials you just registered.

## Step 5: Home Page
- Once logged in, you will be redirected to the home page. Here you can see the current status of the hub and the enviroment. You should see the camera feed, the analysis results, a "Templates" card, an LED switch, and the sensor readings. On startup there will be no analysis results, no templates, the LED switch will be disabled, and the sensor readings will be empty.

## Step 6: LED
- Plug in the LED to the power supply. The LED should automatically find the hub (over mDNS) and connect to it. Once connected, the LED switch on the home page should become enabled. This can take upto 5 seconds, alternatively you can refresh the page. You can now use the LED switch to turn the LED on and off. The LED is controlled by the webserver. If testing between 8:00 and 20:00, the LED will automatically turn on (since this is the default setting).

## Step 7: Sensor Readings & Pumps
- Plug in the pumps to the power supply. Then plug in the Ardunio's to a USB port (for power). This can be done using the USB port of the PC on the window sill. The sensors and pumps should automatically find the hub (over mDNS) and connect to it. Once connected, the sensor readings on the home page should be updated. This can take upto 5 seconds, alternatively you can refresh the page. You can now see the sensor readings and the pumps should be working.

## Step 8: Pumps
- The decision was made to not be able to control the pumps over the webpage. The pumps are controlled by the autocontroller, which is running on the hub. The autocontroller will automatically turn the pumps on and off based on the sensor readings. The autocontroller is running 24/7 and does not need any user input. It checks the sensor readings every 60 minutes and turns the pumps on and off accordingly. If the maximum waterlevel is reached, toggle commands to any pump will simply be ignored.

## Step 9: Templates
- The templates are used to adjust the settings for the autocontroller. The autocontroller has an internal default template, which is used when no other template exists. This default template can not be deleted. You can create a new template by clicking on the `Create template` button. A modal will pop up, where you can fill in the required details. The input fields of the creation modal are already filled with the autocontrollers internal default values. After creating the **first** template it will get activated. The active template is used by the autocontroller. At this point there will always be at least one user generated template and the internal default template will never be used again. One can switch between active templates by clicking on the `Set as active` button. One can also delete a template by clicking on the `Delete template` button. One can not delete the active template.

## History
- The webpage has a history page, where you can see the history of the sensor readings and the pump status. To select a date, click on the date picker and select the date you want to see the history of. The history will be displayed below the date picker.
One can also download the history data in various formats such as CSV.

## Log
- The webpage has a log page, where you can see the log of autocontroller. One can sort and filter the log. One can also download the log.