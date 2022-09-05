#!/usr/bin/python3

"""
main program for generating building profiles
Authors: Andrej Campa, Denis Sodin
"""

# for building part
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from configLoader import *
import variables
import json
import requests

sys.path.append('./alpg')
import profilegentools


from building_model import *

matplotlib.style.use('ggplot')

# remove all old outputs from file
diro = 'output'
for f in os.listdir(diro):
    os.remove(os.path.join(diro, f))


# we use default COP (coefficient of performance) curve from here as reference
# https://tisto.eu/images/thumbnails/1376/1126/detailed/5/toplotna-crpalka-zrak-voda-18-6-kw-monoblok-400-v-25-c-r407c-5025-tisto.png
# this curve can be shifted up and down, we use the 55 degrees curve, air-to-water heat pump!
def HVAC_COP(temp, shift_COP_number=0.0):
    """
    only for heating!
    :param temp: outside air temperature, since this is air watter
    :param shift_COP_number: shift COP number to test more or less efficient system using same shape
    :return: return single value COP at specific temperature
    """

    # fitted curve to third order polynom
    Heat_COP = shift_COP_number + 2.6288 + 5.458e-2 * temp - 2.705e-4 * temp ** 2 + 3.795e-5 * temp ** 3
    # only electric heater is on!
    if Heat_COP < 1.0:
        Heat_COP = 1.0
    return Heat_COP


# COP for cooling
# https://www.researchgate.net/figure/Thermal-performance-curve-of-the-normal-air-conditioner_fig2_266975980
def airconditioner_COP(Tamb, Temp, shift_COP_number=0.0):
    """
    only for cooling!
    :param Tamb: Ambient temperature
    :param Temp: Outdoor temperature
    :param shift_COP_number: shift COP number to test more or less efficient system using same shape
    :return: return single value COP at specific temperature
    """
    if Tamb < Temp:
        Cool_COP = shift_COP_number + 5.7915 - 0.2811 * (Temp - Tamb)
    else:
        Cool_COP = np.nan
    if Cool_COP < 1:
        Cool_COP = 1.0
    return Cool_COP


# business building
# need to generate statistically consumption
def business_building_profile(background_power, peak_power, office_hours=[9 * 60, 17 * 60], weekend=False):
    """
    :param background_power: consumption power of all appliances in the building that can not be turned on or off [W]
    :param peak_power: peak consumption power when all employees are presented in their workplace [W]
    :param office hours: typical starting and ending hour of the workday in minutes - array [start,stop]
    :param weekend: only background power is considered - bool
    :return: 15 min series of the building metered power [kW]
    """
    consumption = np.ones(24 * 4, dtype=np.float64) * background_power
    if not weekend:
        for t_min in range(24 * 4):  # in this case hour is actualy 15 min interval
            consumption[t_min] = consumption[t_min] \
                                 + (peak_power - background_power) * 1.0 / (1.0 + np.exp(-t_min + office_hours[0] / 15)) \
                                 - (peak_power - background_power) * 1.0 / (1.0 + np.exp(-t_min + office_hours[1] / 15))
    return consumption


##################
#### PV MODEL ####
##################
def getPVprofile(m=6, latitude=46.056946, longitude=14.505751, surface_tilt=35, surface_azimuth=0, usehorizon=0,
                 nglobal=1, outputformat='json'):
    """
    :param m: month of a year [1,12]
    :param latitude: degrees, decimal
    :param longitude: degrees, decimal
    :param surface_tilt: PV tilt/inclination degrees
    :param surface_azimuth: The azimuth, or orientation, is the angle of the PV modules relative to the direction due
            South. - 90° is East, 0° is South and 90° is West.
    :param usehorizon: if usehorizon=0 means getting data without taking into account the horizon, if usehorizon=1
        means getting data with taking into account the horizon.
    :param nglobal: Output the global and diffuse in-plane irradiances. Value of 1 for "yes". All other values
        (or no value) mean "no". Default=1.
    :param outputformat: string with the format of data, default='json'
    :return: dataframe with temperatures and radiations daily profiles typical for particular month
    """

    URL_BASE = 'https://re.jrc.ec.europa.eu/api/DRcalc?'
    prova = 'lat=' + str(latitude) + '&lon=' + str(longitude) + '&month=' + str(m) + '&angle=' + str(
        surface_tilt) + '&aspect=' + str(surface_azimuth) + '&usehorizon=' + str(usehorizon) + '&global=' + str(
        nglobal) + '&localtime=0' + '&showtemperatures=1' + '&outputformat=' + str(outputformat)
    URL = URL_BASE + prova
    jsn = requests.get(URL)
    pvgis_json = json.loads(jsn.text)
    data = pd.json_normalize(pvgis_json['outputs']['daily_profile'])
    test = data.iloc[[0]]
    test.at[0, 'time'] = '23:59'
    data = pd.concat([data, test])
    data = data.set_index('time')
    data.index = pd.to_datetime(data.index)
    data = data.fillna(0)
    data = data.resample('15min').asfreq()
    data = data.interpolate()
    data = data.fillna(method='ffill')
    return data

def solar_power_taking_account_temperature(temperature, irradiance, Wp=5000, system_losses=0.2, NOCT=45,
                                           coef_t=-0.47 / 100, stc_irradiance=1000):
    """
        Wp - peak nominal power of PV
        :param t_amb: Series of the ambient temperature.
        :param irradiance: Series of the POA GHI
        :param system_losses: Value of system losses, default= 0.15
        :param NOCT: Nominal Operating Cell Temperature, default=44
        :param coef_t: Coefficient temperature of the model, default=-0.38/100
        :param stc_irradiance: Standard test condition irradiance, default=1000
        :return: Series with the output power of the PV system [kW]
        """
    t_cell = temperature + (irradiance * 0.00125) * (NOCT - 20)
    # t_cell=t_amb+(irradiance/800)*(NOCT-20)
    P = (Wp / stc_irradiance) * irradiance * (1 - system_losses) * (1 + (t_cell - 25) * (coef_t))  # *0.001
    P = P.fillna(0)
    return P



#############
# main part #
#############

# get typical irradiance and temperatures for PV and building model
PVdata = getPVprofile(m=variables.m, latitude=variables.latitude, longitude=variables.longitude, surface_tilt=variables.tiltPV, surface_azimuth=variables.azimuthPV)
temperature = PVdata["T2m"]
irradiance = PVdata["G(i)"]  # global irradiance on a fixed plane
direct = PVdata["Gb(i)"]  # Direct irradiance on a fixed plane
difuse = PVdata["Gd(i)"]  # diffuse irradiance on a fixed plane

# Calculate the actual PV power based on irradiance on the Plane of array (POA)
PVpower = solar_power_taking_account_temperature(temperature, irradiance, Wp=variables.PV_nominal_power)
PVpower = [i for i in PVpower]  # make list without timestamps



################################
#### Load profile generator ####
################################

# import houses_matrycs
config = importlib.import_module(cfgFile)

print('Loading config: ' + cfgFile, flush=True)
print("The current config will create and simulate " + str(len(config.householdList)) + " households", flush=True)
print("Results will be written into: " + cfgOutputDir + "\n", flush=True)
print("NOTE: Simulation may take a (long) while...\n", flush=True)

# Check the config:
if config.penetrationEV + config.penetrationPHEV > 100:
    print("Error, the combined penetration of EV and PHEV exceed 100!", flush=True)
    exit()
if config.penetrationPV < config.penetrationBattery:
    print("Error, the penetration of PV must be equal or higher than PV!", flush=True)
    exit()
if config.penetrationHeatPump + config.penetrationCHP > 100:
    print("Error, the combined penetration of heatpumps and CHPs exceed 100!", flush=True)
    exit()

# Randomize using the seed
random.seed(config.seed)

# Create empty files
config.writer.createEmptyFiles()

# import neighbourhood
import neighbourhood

neighbourhood.neighbourhood()

hnum = 0

householdList = config.householdList
print("this is householdlist", householdList)
numOfHouseholds = len(householdList)

# original script iterates through alpg houses here, we only take 1 representative house

print("Household " + str(hnum + 1) + " of " + str(numOfHouseholds), flush=True)
householdList[0].simulate()

# Warning: On my PC the random number is still the same at this point, but after calling scaleProfile() it isn't!!!
householdList[0].scaleProfile()
householdList[0].reactivePowerProfile()
householdList[0].thermalGainProfile()

config.writer.writeHousehold(householdList[0], hnum)
config.writer.writeNeighbourhood(hnum)

globals()['DeviceGain{}'.format(hnum + 1)] = householdList[0].HeatGain["DeviceGain"]
globals()['PersonGain{}'.format(hnum + 1)] = householdList[0].HeatGain["PersonGain"]
globals()['Consumption{}'.format(hnum + 1)] = householdList[0].Consumption["Total"]

# building
# Empty Lists for Storing Data to Plot
ElectricityOut = []
HeatingDemand = []  # Energy required by the zone
HeatingEnergy = []  # Energy required by the supply system to provide HeatingDemand
CoolingDemand = []  # Energy surplus of the zone
CoolingEnergy = []  # Energy required by the supply system to get rid of CoolingDemand
IndoorAir = []
OutsideTemp = []
SolarGains = []
COP = []

gain_per_person = globals()['PersonGain{}'.format(hnum + 1)]  # W per person
appliance_gains = globals()['DeviceGain{}'.format(hnum + 1)]  # W per sqm

from resample import *  # resample the data from minute to 15 interval

consumption_total_resampled = df_new["agregated"]

###########################################
##### Building model - heating cooling ####
###########################################
# Initialise an instance of the building

walls_area=500
house = Building(window_area=20.0,
                 walls_area=500.0,
                 floor_area=180.0,
                 volume_building=414,
                 U_walls=0.2,
                 U_windows=1.1,
                 ach_vent=0.35,
                 ventilation_efficiency=0.6,
                 thermal_capacitance_per_floor_area=165000,
                 t_set=22.0,
                 latitude=latitude,
                 longitude=longitude)

# get sout window irradiance, that is used in the daily loop
south_window_azimuth =0
windows_tilt = 90
south_window = getPVprofile(m=m, surface_tilt=windows_tilt, surface_azimuth=south_window_azimuth)
irradiance_south_direct = south_window["Gb(i)"]  # Direct irradiance on a fixed plane
irradiance_south_diff = south_window["Gd(i)"]

# Loop through  24*4 (15 min intervals) of the day
for hour in range(
        24 * 4):  # in this case hour is actualy 15 min interval, therefore calc_sun_position in radiation.py needs to be modified

    # Gains from occupancy and appliances
    house.internal_gains = gain_per_person[hour] + appliance_gains[hour]

    # Extract the outdoor temperature
    t_out = temperature[hour]
    # reset solar gains after the reset add as many different windows as needed
    house.solar_gains = 0.0
    house.solar_power_gains(window_area = 10,
                            irradiance_dir = irradiance_south_direct[hour],
                            irradiance_dif = irradiance_south_diff[hour],
                            month=m,
                            hour=hour,
                            tilt=windows_tilt,
                            azimuth = south_window_azimuth,
                            transmittance=0.7,
                            )
    house.calc_heat_demand(t_out)

    HeatingDemand.append(house.heat_demand)
    OutsideTemp.append(t_out)
    SolarGains.append(house.solar_gains)

dailyResults = pd.DataFrame({
    'HeatingDemand': HeatingDemand,
    'OutsideTemp': OutsideTemp,
    'SolarGains': SolarGains,
})

dailyResults[['HeatingDemand']].plot()
plt.show()

dailyResults[['OutsideTemp']].plot()
plt.show()

###############################
# Business Building el. model #
###############################
bus_profile = business_building_profile(1000, 5000, office_hours=[9 * 60, 17 * 60], weekend=False)


######################
# Electric vehicle
######################
from EV import charging_profile, EV_startTimes, EV_endTimes

######################
# Plot all profiles
######################
plt.plot(charging_profile, label='Electric vehicle', color='m')  # Power [W]
plt.plot(bus_profile, label='business building', color='y')  # Power [W]
plt.plot(HeatingDemand, label='heating demand', color='r')  # Power [Wh/h]
plt.plot(CoolingDemand, label='cooling demand', color='b')  # Power [Wh/h]
plt.plot(PVpower, label='PV', color='g')  # Power [W]
plt.plot(consumption_total_resampled, label='Consumption', color='k')  # Power [W]
plt.grid()
plt.legend()
plt.ylabel('power consumption [W]')
plt.xlabel('time 15min slices')
plt.show()

#################################
# Times for heating and cooling #
# if daily cooling and heating is not exceeding the 1 degree of total thermal capacitance, we neglect it!
# Steps:
# 1. calculate thermal heat-capacitance of building/house for 1 degree celsius difference
#################################

energy_limit = thermal_capacitance / (60 * 60) * flor_area  # Wh
sum_energy_needed = 0
list_of_times = [0]
list_of_energies = []
for hour in range(24 * 4):
    sum_energy_needed += HeatingDemand[hour] / 4.0 # divided by 4 since we are
    # operating with energy on timeslice of 15 minutees
    if sum_energy_needed > energy_limit:
        sum_energy_needed -= energy_limit  # transfer rest of the energy to next time slice
        list_of_times.append(hour)
        list_of_energies.append(energy_limit)
    elif sum_energy_needed < -energy_limit:
        sum_energy_needed += energy_limit
        list_of_times.append(hour)
        list_of_energies.append(energy_limit)
list_of_times.append(96)
list_of_energies.append(sum_energy_needed)

print('The End')
