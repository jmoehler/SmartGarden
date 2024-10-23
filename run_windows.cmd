@echo off

rem Set the base directory where the scripts are located
set BASE_DIR=%~dp0

rem Execute the Python files in separate command prompt windows with a delay
start cmd /k python "%BASE_DIR%hub\main.py"
timeout /nobreak /t 3 >nul
start cmd /k python "%BASE_DIR%simulators\sensor_simulator.py"
timeout /nobreak /t 3 >nul
start cmd /k python "%BASE_DIR%simulators\actuator_simulator.py"

rem Pause to keep the console window open
pause
