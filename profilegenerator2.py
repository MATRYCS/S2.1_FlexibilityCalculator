#!/usr/bin/python3

# Artifical load profile generator v1.2, generation of artificial load profiles to benchmark demand side management approaches
# Copyright (C) 2018 Gerwin Hoogsteen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# for building part
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from configLoader import *
from variables import *

sys.path.insert(0, './alpg')
import profilegentools
import requests
import json

# from RC_BuildingSimulator.rc_simulator.building_physics import Zone  # Importing Zone Class
sys.path.insert(0, './RC_BuildingSimulator/rc_simulator')
# import building_physics
from building_physics import *
from radiation import Location
from radiation import Window

matplotlib.style.use('ggplot')


# business building
# need to generate statistically consumption

def business_building_profile(background_power, peak_power, office_hours=[9 * 60, 17 * 60], weekend=False):
    """
    :param background_power: consumption power of all appliances in the building that can not be turned on or off [W]
    :param peak_power: peak consumption power when all employees are presented in their workplace [W]
    :param office hours: typical starting and ending hour of the workday in minutes
    :param weekend: only background power is considered
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
        m - month of a year [1,12]
        surface_tilt - angle of the PV modules from the horizontal plane
        surface_azimuth - The azimuth, or orientation, is the angle of the PV modules relative to the direction due South. - 90° is East, 0° is South and 90° is West.
        usehorizon - if usehorizon=0 means getting data without taking into account the horizon, if usehorizon=1
        means getting data with taking into account the horizon.
        nglobal - Output the global and diffuse in-plane irradiances. Value of 1 for "yes". All other values
        (or no value) mean "no". Default=1.
        outputformat - string with the format of data, default='json'
        """

    URL_BASE = 'https://re.jrc.ec.europa.eu/api/DRcalc?'
    prova = 'lat=' + str(latitude) + '&lon=' + str(longitude) + '&month=' + str(m) + '&angle=' + str(
        surface_tilt) + '&aspect=' + str(surface_azimuth) + '&usehorizon=' + str(usehorizon) + '&global=' + str(
        nglobal) + '&localtime=0' + '&showtemperatures=1' + '&outputformat=' + str(outputformat)
    URL = URL_BASE + prova
    print(URL)
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


# calculate irradiance for later use in the PV modul
PVdata = getPVprofile(m=m, latitude=latitude, longitude=longitude, surface_tilt=tiltPV, surface_azimuth=azimuthPV)
temperature = PVdata["T2m"]
irradiance = PVdata["G(i)"]  # global irradiance on a fixed plane
direct = PVdata["Gb(i)"]  # Direct irradiance on a fixed plane
difuse = PVdata["Gd(i)"]  # diffuse irradiance on a fixed plane


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


# Calculate the actual PV power based on irradiance on the Plane of array (POA)
PVpower = solar_power_taking_account_temperature(temperature, irradiance, Wp=PV_nominal_power)


#############################
#### end of the PV MODEL ####
#############################


# t_m_prev previous temperature used for next time stamp
# All other data is obtained from PVGIS, irradiance, outside temperature,...!
def get_building_profile(buildingType, year, t_m_prev):
    # Loop through  24*4 (15 min intervals) of the day
    for hour in range(
            24 * 4):  # in this case hour is actualy 15 min interval, therefore calc_sun_position in radiation.py needs to be modified

        # Gains from occupancy and appliances
        internal_gains = gain_per_person[hour] + appliance_gains[hour]

        # Extract the outdoor temperature in Zurich for that hour
        # t_out = Zurich.weather_data['drybulb_C'][hour]
        t_out = temperature[hour]

        Altitude, Azimuth = village.calc_sun_position(latitude, longitude, year, hoy=hour)

        SouthWindow.calc_solar_gains(sun_altitude=Altitude, sun_azimuth=Azimuth,
                                     normal_direct_radiation=direct[hour],
                                     horizontal_diffuse_radiation=difuse[hour])

        # we dont have illuminance data
        # SouthWindow.calc_illuminance(sun_altitude=Altitude, sun_azimuth=Azimuth,
        #                              normal_direct_illuminance=Zurich.weather_data[
        #                                  'dirnorillum_lux'][hour],
        #                              horizontal_diffuse_illuminance=Zurich.weather_data['difhorillum_lux'][hour])

        buildingType.solve_energy(internal_gains=internal_gains,
                                  solar_gains=SouthWindow.solar_gains,
                                  t_out=t_out,
                                  t_m_prev=t_m_prev)

        # Office.solve_lighting(
        #     illuminance=SouthWindow.transmitted_illuminance, occupancy=occupancy)

        # Set the previous temperature for the next time step
        t_m_prev = buildingType.t_m_next

        HeatingDemand.append(buildingType.heating_demand)
        HeatingEnergy.append(buildingType.heating_energy)
        CoolingDemand.append(buildingType.cooling_demand)
        CoolingEnergy.append(buildingType.cooling_energy)
        ElectricityOut.append(buildingType.electricity_out)
        IndoorAir.append(buildingType.t_air)
        OutsideTemp.append(t_out)
        SolarGains.append(SouthWindow.solar_gains)
        COP.append(buildingType.cop)

    annualResults = pd.DataFrame({
        'HeatingDemand': HeatingDemand,
        'HeatingEnergy': HeatingEnergy,
        'CoolingDemand': CoolingDemand,
        'CoolingEnergy': CoolingEnergy,
        'IndoorAir': IndoorAir,
        'OutsideTemp': OutsideTemp,
        'SolarGains': SolarGains,
        'COP': COP
    })
    return annualResults


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

########################################
#### RC simulator - heating cooling ####
########################################
# Initialise an instance of the Zone. Empty spaces take on the default
# parameters. See ZonePhysics.py to see the default values
office = Zone(window_area=4.0,
              walls_area=11.0,
              floor_area=35.0,
              room_vol=105,
              total_internal_area=142.0,
              lighting_load=11.7,
              lighting_control=300.0,
              lighting_utilisation_factor=0.45,
              lighting_maintenance_factor=0.9,
              u_walls=0.2,
              u_windows=1.1,
              ach_vent=1.5,
              ach_infl=0.5,
              ventilation_efficiency=0.6,
              thermal_capacitance_per_floor_area=165000,
              t_set_heating=20.0,
              t_set_cooling=25.0,
              max_cooling_energy_per_floor_area=-np.inf,
              max_heating_energy_per_floor_area=np.inf,
              heating_supply_system=supply_system.OilBoilerMed,
              cooling_supply_system=supply_system.HeatPumpAir,
              heating_emission_system=emission_system.NewRadiators,
              cooling_emission_system=emission_system.AirConditioning, )

house = Zone(window_area=15,
             walls_area=608,  # 2,8*10*8*2 + 80*2
             floor_area=160.0,
             room_vol=368,  # 2.3*160
             total_internal_area=1,
             lighting_load=11.7,
             lighting_control=300.0,
             lighting_utilisation_factor=0.45,
             lighting_maintenance_factor=0.9,
             u_walls=0.2,
             u_windows=1,
             ach_vent=1.5,
             ach_infl=0.5,
             ventilation_efficiency=0.6,
             thermal_capacitance_per_floor_area=165000,
             # Very light: 80 000 Light: 110 000 Medium: 165 000 Heavy: 260 000 Very heavy:370 000
             t_set_heating=20.0,
             t_set_cooling=25.0,
             max_cooling_energy_per_floor_area=-np.inf,
             max_heating_energy_per_floor_area=np.inf,
             heating_supply_system=supply_system.OilBoilerMed,
             cooling_supply_system=supply_system.HeatPumpAir,
             heating_emission_system=emission_system.NewRadiators,
             cooling_emission_system=emission_system.AirConditioning, )

# Define Windows
SouthWindow = Window(azimuth_tilt=0, alititude_tilt=90, glass_solar_transmittance=0.7,
                     glass_light_transmittance=0.8, area=4)

# A catch statement to prevent future coding bugs when modifying window area
if SouthWindow.area != office.window_area:
    raise ValueError('Window area defined in radiation file doesnt match area defined in zone')

village = Location('houses')

# iterate through alpg houses
while len(householdList) > 0:
    print("Household " + str(hnum + 1) + " of " + str(numOfHouseholds), flush=True)
    # print(householdList[0])
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

    # get results for 1 day RC-simulator of the building! not same as households!!!!
    dailyResults = get_building_profile(house, year=2015, t_m_prev=21)

    # Plotting 
    # dailyResults[['HeatingEnergy', 'CoolingEnergy']].plot()
    # plt.show()

    # dailyResults[['HeatingDemand', 'CoolingDemand']].plot()
    # plt.show()

    # dailyResults[['IndoorAir', 'OutsideTemp']].plot()
    # plt.show()

    householdList[0].Consumption = None
    householdList[0].Occupancy = None
    for p in householdList[0].Persons:
        del (p)
    del (householdList[0])

    hnum = hnum + 1

######################
# Building el. model #
######################
bus_profile = business_building_profile(10000, 50000, office_hours=[9 * 60, 17 * 60], weekend=False)

np.array
plt.plot(bus_profile)
plt.ylabel('business building consumption power [W]')
plt.xlabel('time 15min slices')
plt.show()

print('The End')
