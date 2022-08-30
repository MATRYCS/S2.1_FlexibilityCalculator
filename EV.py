# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 09:48:39 2022

@author: DSodin
"""
from resample import *
with open(r'output\ElectricVehicle_Starttimes.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list 
    for startTime in file:
        EV_string = startTime.split(":")[1] #get all the ending times as a string of starting times
        EV_list = EV_string.split(",") #make a list of strings; each string its own starting time
        EV_startTimes = [(int(x)-offset) for x in EV_list] 

with open(r'output\ElectricVehicle_Endtimes.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list 
    for endTime in file:
        EV_string = endTime.split(":")[1] 
        EV_list = EV_string.split(",") 
        EV_endTimes = [int(x) - offset for x in EV_list]
       

with open(r'output\ElectricVehicle_Specs.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list 
    for spec in file:
        specs = spec.split(":")[1]
        capacity = int(specs.split(",")[0]) #battery capacity
        charge_power = int(specs.split(",")[1])
        
with open(r'output\ElectricVehicle_RequiredCharge.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list 
    for charge in file:
        charges = charge.split(":")[1]
        charge = float(charges.split(",")[0]) #required charge
        
        
if len(EV_startTimes)==0:
    charging_profile = [0]*96
    print("EV file is empty")
else:    
    for i in range(len(EV_startTimes)):
        charge_time = round(charge/charge_power*60.0/15.0)
        # print("charge time is" , charge_time)
        starting_charging_moment = random.randint(EV_startTimes[i], EV_endTimes[i]-charge_time)
        if starting_charging_moment >= 1440:
            starting_charging_moment -= 1440
        starting_charging_moment = round(starting_charging_moment/15)
        charging_profile = [0]*96
        count = 0
        while charge_time > 0:  
            if starting_charging_moment+count >= 96: #if you charge over midnight you need to subtract 1 day
                starting_charging_moment -= 96
            charging_profile[starting_charging_moment+count] = charge_power
            # print(count+starting_charging_moment)
            count += 1
            charge_time -= 1

    