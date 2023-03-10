#!/usr/bin/python3
"""
main program for generating building profiles
Authors: Andrej Campa, Denis Sodin

example:
import profilegenerator2
use_case = profilegenerator2.profilgenerator2()
use_case.calculation(house_type)
print(use_case.tiltPV)

"""

# for building part
import sys
import os
import random
import json
import requests
import numpy as np
import pandas as pd
#import importlib

sys.path.append('./configs')
import houses_matrycs

sys.path.append('./alpg')
import profilegentools
import writer

from building_model import *

#import neighbourhood
import houses_matrycs

folder = 'output'

cfgOutputDir = 'output'
cfgFile = 'houses_matrycs'


class profilgenerator2():
    """
    alpg library modified to class
    """

    def __init__(self,
                 month=1, # month of the year 1-January
                 latitude=45.0,
                 longitude=14.0,
                 timezone='Europe/Ljubljana',
                 PV_nominal_power=5000,
                 tiltPV=35,
                 azimuthPV=0,
                 window_area=20.0,
                 walls_area=500.0,
                 floor_area=180.0,
                 volume_building=414,
                 U_walls=0.2,
                 U_windows=1.1,
                 ach_vent=0.35,
                 ventilation_efficiency=0.6,
                 thermal_capacitance=165000,
                 t_set=22.0,
                 south_window_area=10,
                 south_window_azimuth = 0,
                 windows_tilt = 90,
                 background_consumption=1000,
                 peak_consumption = 5000,
                 office_start_t = 9 * 60,  # minutees
                 office_end_t = 17 * 60,
                 weekend=False, # startday True-weekend False-working day
                 bat_capacity = 10000, # Wh
                 bat_power = 3000,  # W charging discarging power
                 bat_efficiency = 0.9,  # return efficiency of the battery
                 heating_type=1,  # 1-HVAC, 2-el. heater, 3-other, not used for estimating electric consumption
                 cooling_type = 1,  # 1- air-conditioner, 2-other not used for estimating electric consumption
                 EV_capacity = 30000,  # [Wh]
                 EV_power = 3000,  # [W] maks charging power
                 hasEV = True,
                 commute_distance_EV = 25,
                 heating_el_P = 3000,
                 cooling_el_P = 2000,
                 ):
        self.month = month
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.PV_nominal_power = PV_nominal_power
        self.tiltPV = tiltPV
        self.azimuthPV = azimuthPV
        self.window_area = window_area  # [m2] Window Area
        self.walls_area = walls_area
        self.floor_area = floor_area
        self.volume_building = volume_building
        self.U_walls = U_walls
        self.U_windows = U_windows
        self.ach_vent = ach_vent
        self.ventilation_efficiency = ventilation_efficiency
        self.thermal_capacitance = thermal_capacitance
        self.t_set = t_set
        self.solar_gains = 0.0
        self.internal_gains = 0.0
        self.heat_demand = 0.0
        self.angle_incidence = 0.0
        self.transmittance = 1.0
        self.south_window_area = south_window_area
        self.south_window_azimuth = south_window_azimuth
        self.windows_tilt = windows_tilt
        self.background_consumption = background_consumption
        self.peak_consumption = peak_consumption
        self.office_start_t = office_start_t  # minutees
        self.office_end_t = office_end_t
        self.weekend = weekend  # startday 1-weekend 2-working day
        self.bat_capacity = bat_capacity  # Wh
        self.bat_power = bat_power  # W charging discarging power
        self.bat_efficiency = bat_efficiency  # return efficiency of the battery
        self.heating_type = heating_type  # 1-HVAC, 2-el. heater, 3-other, not used for estimating electric consumption
        self.cooling_type = cooling_type  # 1- air-conditioner, 2-other not used for estimating electric consumption
        self.EV_capacity = EV_capacity  # [Wh]
        self.EV_power = EV_power  # [W] maks charging power
        self.df_new = None
        self.PVpower = np.zeros(96)
        self.PVdata = np.zeros(96)
        self.EV_startTimes = []
        self.EV_endTimes = []
        self.charging_profile = []
        self.list_of_times_HVAC = []
        self.list_of_energies_HVAC = []
        self.house_type = "Single worker"
        self.com_build_on = "private house"
        self.bus_profile = np.zeros(96)
        self.consumption_total_resampled = np.zeros(96)
        self.hasEV = hasEV
        self.commute_distance_EV = commute_distance_EV
        self.df_el = []
        self.heating_el_P = heating_el_P
        self.cooling_el_P = cooling_el_P
        self.energies_heating = 0
        self.energies_cooling = 0

    # we use default COP (coefficient of performance) curve from here as reference
    # https://tisto.eu/images/thumbnails/1376/1126/detailed/5/toplotna-crpalka-zrak-voda-18-6-kw-monoblok-400-v-25-c-r407c-5025-tisto.png
    # this curve can be shifted up and down, we use the 55 degrees curve, air-to-water heat pump!
    def HVAC_COP(self, temp, shift_COP_number=0.0):
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
    def airconditioner_COP(self, Tamb, Temp, shift_COP_number=0.0):
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
            Cool_COP = shift_COP_number + 5.7915 - 0.2811 * (Temp - Tamb)
        if Cool_COP < 1:
            Cool_COP = 1.0
        return Cool_COP

    def HVAC_el(self):
        """
        Calculates electric demand for heating/cooling
        :return: Electric profile
        :rtype: float, length 24*4 15min sampling

        Modifies Energies cooling, energies heating
         self.energies_heating
         self.energies_cooling
        """
        self.HVAC_kWh = 0
        self.AC_kWh = 0
        HVAC_el_power_profile = np.zeros(96)  # electrical profile of HVAC randomize start!
        for en in self.list_of_energies_HVAC:
            if en > 0:
                self.HVAC_kWh += en
            else:
                self.AC_kWh -= en
        ###########
        # Heating #
        ###########
        # seed for randomizing of turning on and off the HVAC
        seed = random.randrange(96)
        if self.heating_type == 1:
            HVAC_energies = []
            # calculates all energies that HVAC is able to produce at certain time in the day 15min timestamp (hence /4.0)
            for x in range(96):
                HVAC_energies.append(self.HVAC_COP(self.OutsideTemp[x]) * self.heating_el_P / 4.0)
            # calculating HVAC energies
            self.energies_heating = 0
            for i in range(len(self.list_of_times_HVAC)):
                HVAC_profile_temp = []
                t_start = self.list_of_times_HVAC[i - 1]
                t_end = self.list_of_times_HVAC[i]
                if len(self.list_of_times_HVAC) == 1:
                    t_end = 96
                    t_start = 1
                delta = t_end - t_start
                if delta < 0:
                    delta += 96
                # ordered energies for each timestamp, first calculate default value for time and after that optimal
                energies_timestamp = np.roll(HVAC_energies, -t_start)[:delta]
                # not optimized
                list_en = self.list_of_energies_HVAC[i]
                if list_en < 0:
                    continue
                for en in energies_timestamp:
                    if en <= 0:
                        break
                    elif en < list_en:
                        list_en -= en
                        self.energies_heating += self.heating_el_P / 4.0
                        HVAC_profile_temp.append(self.heating_el_P)
                    else:  # only some leftovers
                        self.energies_heating += (list_en / en) * self.heating_el_P / 4.0
                        HVAC_profile_temp.append(self.heating_el_P*(list_en / en))
                        break
                # creating profile
                delta_time_HVAC = len(HVAC_profile_temp)
                t_start = t_start + seed
                if (t_start>95):
                    t_start = t_start-96
                t_hvac = t_start
                for i2 in range(delta_time_HVAC):
                    if t_hvac+i2>95:
                        t_hvac=t_hvac-96
                    HVAC_el_power_profile[t_hvac+i2] = HVAC_el_power_profile[t_hvac+i2]+HVAC_profile_temp[i2]

        elif self.heating_type == 2:
            self.energies_heating = self.HVAC_kWh
            #creating profiles, random start
            for i in range(len(self.list_of_times_HVAC)):
                temp_eng=self.list_of_energies_HVAC[i]
                t_start = self.list_of_times_HVAC[i - 1]
                t_end = self.list_of_times_HVAC[i]
                if len(self.list_of_times_HVAC) == 1:
                    t_end = 96
                    t_start = 1
                delta = t_end - t_start
                if delta < 0:
                    delta += 96
                delta_time_HVAC = int(temp_eng*4.0/self.heating_el_P)
                t_start = t_start + seed
                if (t_start > 95):
                    t_start = t_start - 96
                t_hvac = t_start
                for i2 in range(delta_time_HVAC):
                    if t_hvac + i2 > 95:
                        t_hvac = t_hvac - 96
                    HVAC_el_power_profile[t_hvac + i2] = HVAC_el_power_profile[t_hvac + i2] + self.heating_el_P
                # add reminder
                if t_hvac+delta_time_HVAC > 95:
                    t_hvac = t_hvac - 96
                HVAC_el_power_profile[t_hvac+delta_time_HVAC] = HVAC_el_power_profile[t_hvac+delta_time_HVAC] + (temp_eng*4.0)%self.heating_el_P
        else:
            self.energies_heating = 0

        ###########
        # Cooling #
        ###########
        if self.cooling_type == 1:
            AC_energies = []
            for x in range(96):
                AC_energies.append(
                    -self.airconditioner_COP(self.t_set, self.OutsideTemp[x]) * self.cooling_el_P / 4.0)
            # calculating AC energies
            self.energies_cooling = 0
            for i in range(len(self.list_of_times_HVAC)):
                HVAC_profile_temp = []
                t_start = self.list_of_times_HVAC[i - 1]
                t_end = self.list_of_times_HVAC[i]
                if len(self.list_of_times_HVAC) == 1:
                    t_end = 96
                    t_start = 1
                delta = t_end - t_start
                if delta < 0:
                    delta += 96
                # ordered energies for each timestamp, first calculate default value for time and after that optimal
                energies_timestamp = np.roll(AC_energies, -t_start)[:delta]
                # not optimized
                list_en = self.list_of_energies_HVAC[i]
                if list_en > 0:
                    continue
                for en in energies_timestamp:
                    if en >= 0:
                        break
                    elif en > list_en:
                        list_en -= en
                        self.energies_cooling += self.cooling_el_P / 4.0
                        HVAC_profile_temp.append(self.cooling_el_P)
                    else:  # only some leftovers
                        self.energies_cooling += (list_en / en) * self.cooling_el_P / 4.0
                        HVAC_profile_temp.append(self.cooling_el_P * (list_en / en))
                        break
                # creating profile
                delta_time_HVAC = len(HVAC_profile_temp)
                t_start = t_start + seed
                if (t_start > 95):
                    t_start = t_start - 96
                t_hvac = t_start
                for i2 in range(delta_time_HVAC):
                    if t_hvac + i2 > 95:
                        t_hvac = t_hvac - 96
                    HVAC_el_power_profile[t_hvac + i2] = HVAC_el_power_profile[t_hvac + i2] + HVAC_profile_temp[i2]
        else:
            self.energies_cooling = 0
        return HVAC_el_power_profile

    # business building
    # need to generate statistically consumption
    def business_building_profile(self, background_power, peak_power, office_hours=[9 * 60, 17 * 60], weekend=False):
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
    def getPVprofile(self, m=6, latitude=46.056946, longitude=14.505751, surface_tilt=35, surface_azimuth=0, usehorizon=0,
                     nglobal=1, outputformat='json'):
        """
        :param m: month of a year [1,12]
        :param latitude: degrees, decimal
        :param longitude: degrees, decimal
        :param surface_tilt: PV tilt/inclination degrees
        :param surface_azimuth: The azimuth, or orientation, is the angle of the PV modules relative to the direction due
                South. - 90?? is East, 0?? is South and 90?? is West.
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

    def solar_power_taking_account_temperature(self,temperature, irradiance, Wp=5000, system_losses=0.2, NOCT=45,
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
    
    def EVprofile(self):
        EV_startTimes=[]
        EV_endTimes=[]
        if self.weekend:
            offset = 0* 24 * 60
        else:
            offset = 1 * 24 * 60
        with open(r'output/ElectricVehicle_Starttimes.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list
            for startTime in file:
                EV_string = startTime.split(":")[1]  # get all the ending times as a string of starting times
                EV_list = EV_string.split(",")  # make a list of strings; each string its own starting time
                EV_startTimes = [(int(x) - offset) for x in EV_list]

        with open(r'output/ElectricVehicle_Endtimes.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list
            for endTime in file:
                EV_string = endTime.split(":")[1]
                EV_list = EV_string.split(",")
                EV_endTimes = [int(x) - offset for x in EV_list]

        with open(r'output/ElectricVehicle_RequiredCharge.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list
            for charge in file:
                charges = charge.split(":")[1]
                charge = float(charges.split(",")[0])  # required charge

        if len(EV_startTimes) == 0:
            charging_profile = [0.0] * 96
        else:
            for i in range(len(EV_startTimes)):
                charge_time = round(charge / self.EV_power * 60.0 / 15.0)
                starting_charging_moment = random.randint(EV_startTimes[i], EV_endTimes[i] - charge_time)
                if starting_charging_moment >= 1440:
                    starting_charging_moment -= 1440
                starting_charging_moment = round(starting_charging_moment / 15)
                charging_profile = [0.0] * 96
                count = 0
                while charge_time > 0:
                    if starting_charging_moment + count >= 96:  # if you charge over midnight you need to subtract 1 day
                        starting_charging_moment -= 96
                    charging_profile[starting_charging_moment + count] = self.EV_power
                    count += 1
                    charge_time -= 1
        return EV_startTimes, EV_endTimes, charging_profile

    def resample(self):
        if self.weekend:
            startDay = 0
        else:
            startDay = 1
        offset = startDay * 24 * 60  # how far off you start
        #endTime = (startDay + 1) * 24 * 60  # calculate the last minute of the interval
        interval = 15  # define the interval of resampled values in minutes

        washMachine = "on"  # decide whether to account for washing machines and dishwashers or not, "on" includes them anything else ignores them
        dishWash = "on"

        washMachineProfile = [66.229735, 119.35574, 162.44595, 154.744551, 177.089979, 150.90621, 170.08704, 134.23536,
                              331.837935, 2013.922272, 2032.267584, 2004.263808, 2023.32672, 2041.49376, 2012.8128,
                              2040.140352, 1998.124032, 2023.459776, 1995.309312, 2028.096576, 1996.161024, 552.525687,
                              147.718924, 137.541888, 155.996288, 130.246299, 168.173568, 106.77933, 94.445568, 130.56572,
                              121.9515, 161.905679, 176.990625, 146.33332, 173.06086, 145.07046, 188.764668, 88.4058,
                              117.010432, 173.787341, 135.315969, 164.55528, 150.382568, 151.517898, 154.275128, 142.072704,
                              171.58086, 99.13293, 94.5507, 106.020684, 194.79336, 239.327564, 152.75808, 218.58576,
                              207.109793, 169.5456, 215.87571, 186.858018, 199.81808, 108.676568, 99.930348, 151.759998,
                              286.652289, 292.921008, 300.5829, 296.20425, 195.74251, 100.34136, 312.36975, 287.90921,
                              85.442292, 44.8647]
        dishWasherProfile = [2.343792, 0.705584, 0.078676, 0.078744, 0.078948, 0.079152, 0.079016, 0.078812, 0.941108,
                             10.449, 4.523148, 34.157214, 155.116416, 158.38641, 158.790988, 158.318433, 158.654276,
                             131.583375, 13.91745, 4.489968, 1693.082112, 3137.819256, 3107.713851, 3120.197256,
                             3123.464652, 3114.653256, 3121.27497, 3116.305863, 3106.801566, 3117.703743, 3118.851648,
                             3110.016195, 3104.806122, 1148.154728, 166.342624, 161.205252, 160.049824, 158.772588,
                             158.208076, 157.926096, 157.01364, 112.30272, 11.65632, 17.569056, 4.947208, 4.724016,
                             143.12025, 161.129536, 160.671915, 23.764224, 136.853808, 159.11184, 159.464682, 159.04302,
                             36.68544, 9.767628, 4.902772, 2239.315008, 3116.846106, 3111.034014, 3118.112712, 3111.809778,
                             3113.442189, 3110.529708, 3104.676432, 3101.093424, 3121.076178, 1221.232208, 159.964185,
                             2663.07828, 272.524675, 7.76832, 3.258112, 3.299408, 3.295136, 3.256704, 3.258112, 3.262336,
                             2224.648744, 367.142872, 4.711025]

        startDish = []
        startWash = []

        # extract dishWasher start and end time of operation and generate random start point
        with open(r'output/Dishwasher_Starttimes.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list of all dishwashers
            for dishWasher in file:
                dishWash_num = dishWasher.split(":")[0]  # get the number of house the dishwasher belongs to
                dishWash_string = dishWasher.split(":")[
                    1]  # get all the starting times of this dishwasher as a string of starting times
                dishWash_list = dishWash_string.split(",")  # make a list of strings; each string its own starting time
                dishWashStarts = [int(start) for start in dishWash_list]  # convert strings to integers
                globals()['dishWasher{}'.format(dishWash_num) + 'start'] = dishWashStarts
                for t in dishWashStarts:
                    startDish.append((t) / 60 / 24)

        with open(r'output/Dishwasher_Endtimes.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list
            for dishWasher in file:
                dishWash_num = dishWasher.split(":")[0]  # get the number of house the dishwasher belongs to
                dishWash_string = dishWasher.split(":")[1]  # get all the ending times as a string of ending times
                dishWash_list = dishWash_string.split(",")  # make a list of strings; each string its own ending time
                dishWashEnds = [int(end) - len(dishWasherProfile) for end in
                                dishWash_list]  # subtract len(dishWasherProfile) , because this is the last moment you can start dishwasher
                globals()['dishWasher{}'.format(dishWash_num) + 'end'] = dishWashEnds
                globals()['dishWasher{}'.format(dishWash_num)] = []
                for i in range(len(globals()['dishWasher{}'.format(dishWash_num) + 'end'])):
                    globals()['dishWasher{}'.format(dishWash_num)].append(
                        random.randint(globals()['dishWasher{}'.format(dishWash_num) + 'start'][i],
                                       globals()['dishWasher{}'.format(dishWash_num) + 'end'][
                                           i]))  # make a starting time of each dishwasher cycle as random start time in cylce interval

        # extract WashingMachine start and end time of operation and generate random start point
        with open(r'output/WashingMachine_Starttimes.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list of all WashingMachine
            for WashingMachine in file:
                WashingMachine_num = WashingMachine.split(":")[0]  # get the number of house the WashingMachine belongs to
                WashingMachine_string = WashingMachine.split(":")[
                    1]  # get all the starting times of this WashingMachine as a string of starting times
                WashingMachine_list = WashingMachine_string.split(
                    ",")  # make a list of strings; each string its own starting time
                WashingMachineStarts = [int(start) for start in WashingMachine_list]  # convert strings to integers
                globals()['WashingMachine{}'.format(WashingMachine_num) + 'start'] = WashingMachineStarts
                for t in WashingMachineStarts:
                    startWash.append((t) / 60 / 24)

        with open(r'output/WashingMachine_Endtimes.txt', "r") as datafile:
            file = (datafile.read().split())  # read file in 1 list
            for WashingMachine in file:
                WashingMachine_num = WashingMachine.split(":")[0]
                WashingMachine_string = WashingMachine.split(":")[1]  # get all the ending times as a string of ending times
                WashingMachine_list = WashingMachine_string.split(
                    ",")  # make a list of strings; each string its own ending time
                WashingMachineEnds = [int(end) - len(washMachineProfile) for end in
                                      WashingMachine_list]  # subtract len(WashingMachineProfile) , because this is the last moment you can start washing machine
                globals()['WashingMachine{}'.format(WashingMachine_num) + 'end'] = WashingMachineEnds
                globals()['WashingMachine{}'.format(WashingMachine_num)] = []
                for i in range(len(globals()['WashingMachine{}'.format(WashingMachine_num) + 'end'])):
                    globals()['WashingMachine{}'.format(WashingMachine_num)].append(
                        random.randint(globals()['WashingMachine{}'.format(WashingMachine_num) + 'start'][i],
                                       globals()['WashingMachine{}'.format(WashingMachine_num) + 'end'][i]))

        df = pd.read_csv(r'output/Electricity_Profile.csv', sep=";",
                         header=None)  # read the csv file (put 'r' before the path string to address any special characters in the path, such as '\'). Don't forget to put the file name at the end of the path + ".csv"
        df = df.astype(float)  # pretvori dataframe v float, druga??e dela z integerji
        # to calculate gains from electric consumers without dishwasher and
        self.df_el = df
        header = []
        for i in range(df.shape[1]):  # generiraj ??tevilko householda/userja in jo dodaj v header
            header.append(str(i))

        df.columns = header
        df.head()

        if dishWash == "on":
            for user in range(df.shape[1]):
                try:
                    for startT in globals()['dishWasher{}'.format(user)]:
                        count = 0
                        for currentP in dishWasherProfile:
                            if count + startT - offset >= 1440:  # if the index would go over midnight shift it to the start of the day
                                startT -= 1440
                            df[str(user)][startT + count - offset] += currentP
                            count += 1
                except:
                    print('user', user, 'does not have dishWasher')
        else:
            print("dish washers are not included")

        if washMachine == "on":
            for user in range(df.shape[1]):
                try:
                    for startT in globals()['WashingMachine{}'.format(user)]:
                        count = 0
                        for currentP in washMachineProfile:
                            if count + startT - offset >= 1440:
                                startT -= 1440
                            df[str(user)][startT + count - offset] += currentP
                            count += 1
                except:
                    print('user', user, 'does not have WashingMachine')
        else:
            print("washing machines are not included")

        data_len = df.shape[0]
        num = int(data_len / interval)  # number of bins in new file with average power

        dic = {}
        aggregated = []

        for j in range(df.shape[1]):
            globals()['user{}'.format(j)] = []  # make empty list for each user
            for i in range(num):
                globals()['user{}'.format(j)].append(sum(
                    df[str(j)][i * interval:(i + 1) * interval]) / interval)  # add average power of the specified interval
            dic["user" + str(j)] = globals()['user{}'.format(j)]  # make dictionary of all users

        for i in range(num):
            total = 0
            for j in range(df.shape[1]):
                total += globals()['user{}'.format(j)][i]
            aggregated.append(total)

        dic["agregated"] = aggregated
        self.df_new = pd.DataFrame(dic)  # create pandas data frame from dictionary

        if washMachine == "on" and dishWash == "on":
            file_name = 'output/Electricity_Profile_' + str(interval) + 'min_DishAndWash.csv'
        elif washMachine == "on":
            file_name = 'output/Electricity_Profile_' + str(interval) + 'min_Wash.csv'
        elif dishWash == "on":
            file_name = 'output/Electricity_Profile_' + str(interval) + 'min_Dish.csv'
        else:
            file_name = 'output/Electricity_Profile_' + str(interval) + 'min.csv'

        self.df_new.to_csv(file_name, index=False)

    def calculation_BH(self):
        """
        Calculates for one House/Building el and heating/cooling demand
        :return: daily results: profiles for one Building House
        :rtype: dataframe
        """
        self.HeatingDemand = np.zeros(96)
        self.HeatingDemand = []
        self.HeatingDemand_el = np.zeros(96)
        self.HeatingDemand_el = []
        self.OutsideTemp = np.zeros(96)
        self.SolarGains = np.zeros(96)
        self.charging_profile = np.zeros(96)
        self.bus_profile = np.zeros(96)
        self.PVpower = np.zeros(96)
        self.consumption_total_resampled = np.zeros(96)

        # remove all old outputs from file
        diro = 'output'
        for f in os.listdir(diro):
            os.remove(os.path.join(diro, f))

        # get typical irradiance and temperatures for PV and building model
        self.PVdata = self.getPVprofile(m=self.month, latitude=self.latitude, longitude=self.longitude,
                                        surface_tilt=self.tiltPV, surface_azimuth=self.azimuthPV)
        temperature = self.PVdata["T2m"]

        ################################
        #### Load profile generator ####
        ################################
        if self.com_build_on == "private house":
            config = houses_matrycs.House_types()
            if self.weekend:
                startDay = 0
            else:
                startDay = 1
            config.startDay = startDay
            config.calculation(self.house_type)

            # Create empty files
            writer.createEmptyFiles()

            hnum = 0
            house = config.house
            house.hasEV = self.hasEV

            house.Devices['ElectricalVehicle'].BufferCapacity = self.EV_capacity  # .capacityEV
            house.Devices['ElectricalVehicle'].Consumption = self.EV_power  # powerEV
            house.Persons[0].setDistanceToWork(round(max(0, random.gauss(self.commute_distance_EV, self.commute_distance_EV/4))))
            house.simulate()

            # Warning: On my PC the random number is still the same at this point, but after calling scaleProfile() it isn't!!!
            house.scaleProfile()
            house.reactivePowerProfile()
            house.thermalGainProfile()

            writer.writeHousehold(house, hnum)

            globals()['PersonGain{}'.format(hnum + 1)] = house.HeatGain["PersonGain"]
            globals()['Consumption{}'.format(hnum + 1)] = house.Consumption["Total"]

            # building
            # Empty Lists for Storing Data to Plot
            ElectricityOut = []
            self.OutsideTemp = []
            self.SolarGains = []

            # 1440 everyminute
            gain_per_person = globals()['PersonGain{}'.format(hnum + 1)]  # W per person

            # mean of power is more correct to interpolation
            gain_per_person = np.mean(np.reshape(gain_per_person, (-1,15)),axis=1)

             # electrical appliances contribute 40% heat without dishwasher and washing machine most hot water is thrown away!
            gain_consumption = globals()['Consumption{}'.format(hnum + 1)]
            gain_per_person += 0.4 * np.mean(np.reshape(gain_consumption, (-1,15)),axis=1)
            self.resample()

            self.consumption_total_resampled = self.df_new["agregated"]
        ###############################
        # Business Building el. model #
        ###############################
        elif self.com_build_on == "commercial building":
            self.bus_profile = self.business_building_profile(self.background_consumption, self.peak_consumption,
                                                              office_hours=[self.office_start_t, self.office_end_t],
                                                              weekend=self.weekend)

        ###########################################
        ##### Building model - heating cooling ####
        ###########################################
        # Initialise an instance of the building
        house = Building(window_area=self.window_area,
                         walls_area=self.walls_area,
                         floor_area=self.floor_area,
                         volume_building=self.volume_building,
                         U_walls=self.U_walls,
                         U_windows=self.U_windows,
                         ach_vent=self.ach_vent,
                         ventilation_efficiency=self.ventilation_efficiency,
                         thermal_capacitance_per_floor_area=self.thermal_capacitance,
                         t_set=self.t_set,
                         latitude=self.latitude,
                         longitude=self.longitude)

        # get sout window irradiance, that is used in the daily loop

        south_window = self.getPVprofile(m=self.month, surface_tilt=self.windows_tilt,
                                         surface_azimuth=self.south_window_azimuth)
        irradiance_south_direct = south_window["Gb(i)"]  # Direct irradiance on a fixed plane
        irradiance_south_diff = south_window["Gd(i)"]

        # Loop through  24*4 (15 min intervals) of the day
        self.OutsideTemp = []
        self.SolarGains = []

        for hour in range(
                24 * 4):  # in this case hour is actualy 15 min interval, therefore calc_sun_position in radiation.py needs to be modified

            # Gains from occupancy and appliances
            if self.com_build_on == "private house":
                house.internal_gains = gain_per_person[hour]
            # Extract the outdoor temperature
            t_out = temperature[hour]
            # reset solar gains after the reset add as many different windows as needed
            house.solar_gains = 0.0
            house.solar_power_gains(window_area=self.south_window_area,
                                    irradiance_dir=irradiance_south_direct[hour],
                                    irradiance_dif=irradiance_south_diff[hour],
                                    month=self.month,
                                    hour=hour,
                                    tilt=self.windows_tilt,
                                    azimuth=self.south_window_azimuth,
                                    transmittance=0.7,
                                    )
            house.calc_heat_demand(t_out)

            self.HeatingDemand.append(house.heat_demand)
            self.OutsideTemp.append(t_out)
            self.SolarGains.append(house.solar_gains)

        ######################
        # Electric vehicle
        ######################
        if self.com_build_on == "private house":
            self.EV_startTimes, self.EV_endTimes, self.charging_profile = self.EVprofile()
        else:
            self.charging_profile = np.zeros(96)
        #################################
        # Times for heating and cooling #
        # if daily cooling and heating is not exceeding the 1 degree of total thermal capacitance, we neglect it!
        # Steps:
        # 1. calculate thermal heat-capacitance of building/house for 1 degree celsius difference
        #################################

        energy_limit = self.thermal_capacitance / (60 * 60) * self.floor_area  # Wh
        sum_energy_needed = 0
        self.list_of_times_HVAC = []
        self.list_of_energies_HVAC = []
        for hour in range(24 * 4):
            sum_energy_needed += self.HeatingDemand[hour] / 4.0  # divided by 4 since we are
            # operating with energy on timeslice of 15 minutees
            if sum_energy_needed > energy_limit:
                sum_energy_needed -= energy_limit  # transfer rest of the energy to next time slice
                self.list_of_times_HVAC.append(hour)
                self.list_of_energies_HVAC.append(energy_limit)
            elif sum_energy_needed < -energy_limit:
                sum_energy_needed += energy_limit
                self.list_of_times_HVAC.append(hour)
                self.list_of_energies_HVAC.append(-energy_limit)
        if ((sum_energy_needed < (0.4 * energy_limit)) & (len(self.list_of_energies_HVAC))):
            self.list_of_energies_HVAC[0] += sum_energy_needed
        else:
            self.list_of_times_HVAC.append(96)
            self.list_of_energies_HVAC.append(sum_energy_needed)

        self.dailyResults = pd.DataFrame({
            'HeatingDemand': self.HeatingDemand,
            'HeatingCoolingDemand_el': self.HVAC_el(), # Daily electric profiles for Heating/Cooling
            'OutsideTemp': self.OutsideTemp,
            'SolarGains': self.SolarGains,
            'ElectricVehicle': self.charging_profile,
            'BusinessBuildingProfile': self.bus_profile,
            'Photovoltaic': self.PVpower,
            'ConsumptionHouse': self.consumption_total_resampled
        })
        return self.dailyResults

    def business_EV_profile(self,no_EVs,distance):
        EVprofile = np.zeros(96)
        for i in range(no_EVs):
            EVenergy = random.gauss(18, 2)*1000 # ranodmize EV efficiency 18kW per 100 km
            distance_rand = random.gauss(distance, distance/4) # randomize distance
            diff = self.office_end_t - self.office_start_t
            # EV charging during office hourse, but more to the second half
            starting_time = int(random.gauss(self.office_start_t+2.0*diff/3.0, diff/3.0)/15)
            if starting_time > 95:
                starting_time -= 96
            Energy_needed = distance_rand/100.0*EVenergy
            while Energy_needed > 0:
                Energy_needed -= self.EV_power/4  # divided by 4 due to 15min interval
                if Energy_needed<0:
                    EVprofile[starting_time] += (self.EV_power/4 + Energy_needed) * 4
                else:
                    EVprofile[starting_time] += self.EV_power
                starting_time += 1
                if starting_time > 95:
                    starting_time = 0
        return EVprofile


    def calculation_PV(self):
        self.PVdata = self.getPVprofile(m=self.month, latitude=self.latitude, longitude=self.longitude,
                                        surface_tilt=self.tiltPV, surface_azimuth=self.azimuthPV)
        temperature = self.PVdata["T2m"]
        irradiance = self.PVdata["G(i)"]  # global irradiance on a fixed plane
        PV_power=self.solar_power_taking_account_temperature(temperature,irradiance,Wp=self.PV_nominal_power)
        self.PVpower = [i for i in PV_power] # make list without timestamp
        return self.PVpower