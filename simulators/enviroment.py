import csv
import numpy as np
import os

csv_filename = os.path.join(os.path.dirname(__file__), 'enviroment.csv')

def update_csv(param_name, new_mean, new_variance):
    with open(csv_filename, 'r', newline='') as csvfile:
        rows = list(csv.reader(csvfile, delimiter=';'))
        for row in rows:
            if row[0] == param_name:
                row[1] = str(new_mean)
                row[2] = str(new_variance)

    with open(csv_filename, 'w', newline='') as csvfile:
        csv.writer(csvfile, delimiter=';').writerows(rows)
        
def get_data():
    data = {}
    with open(csv_filename, 'r', newline='') as csvfile:
        for row in csv.reader(csvfile, delimiter=';'):
            data[row[0]] = {'mean': float(row[1]), 'variance': float(row[2])}
            
    return data

############################################################################
#
#   Temperature
#
############################################################################

def get_temp():
    data = get_data()
    temperature = np.random.normal(loc=data['temperature']['mean'], scale=data['temperature']['variance'])
    
    if np.random.rand() < 0.1:  
        update_csv('temperature', data['temperature']['mean'] + np.random.normal(loc=0, scale=0.5), data['temperature']['variance'])
        
    return temperature


def increase_temp():
    data = get_data()
    update_csv('temperature', data['temperature']['mean'] + 0.5, data['temperature']['variance'])


def decrease_temp():
    data = get_data()
    update_csv('temperature', data['temperature']['mean'] - 0.5, data['temperature']['variance'])
    
############################################################################
#
#   Humidity
#
############################################################################

def get_humidity():
    data = get_data()
    humidity = np.random.normal(loc=data['humidity']['mean'], scale=data['humidity']['variance'])
    
    if np.random.rand() < 0.1:  
        update_csv('humidity', data['humidity']['mean'] + np.random.normal(loc=0, scale=5), data['humidity']['variance'])
        
    return humidity

def increase_humidity():
    data = get_data()
    update_csv('humidity', data['humidity']['mean'] + 5, data['humidity']['variance'])
    
def decrease_humidity():
    data = get_data()
    update_csv('humidity', data['humidity']['mean'] - 5, data['humidity']['variance'])
    
############################################################################
#
#   PH
#
############################################################################

def get_ph():
    data = get_data()
    ph = np.random.normal(loc=data['ph']['mean'], scale=data['ph']['variance'])
    
    if np.random.rand() < 0.1:  
        update_csv('ph', data['ph']['mean'] + np.random.normal(loc=0, scale=0.125), data['ph']['variance'])
        
    return ph

def increase_ph():
    data = get_data()
    update_csv('ph', data['ph']['mean'] + 0.125, data['ph']['variance'])
    
def decrease_ph():
    data = get_data()
    update_csv('ph', data['ph']['mean'] - 0.125, data['ph']['variance'])
    
############################################################################
#
#   EC
#
############################################################################

def get_ec():
    data = get_data()
    ec = np.random.normal(loc=data['ec']['mean'], scale=data['ec']['variance'])
    
    if np.random.rand() < 0.1:  
        update_csv('ec', data['ec']['mean'] + np.random.normal(loc=0, scale=0.125), data['ec']['variance'])
        
    return ec

def increase_ec():
    data = get_data()
    update_csv('ec', data['ec']['mean'] + 0.125, data['ec']['variance'])
    
def decrease_ec():
    data = get_data()
    update_csv('ec', data['ec']['mean'] - 0.125, data['ec']['variance'])

