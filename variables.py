#!/usr/bin/python3

####################
# common variables #
####################
# get the irradiance data from the website for a specific location and month
m = 2  # month of the year 1-January
latitude = 46.056946
longitude = 14.505751
timezone = 'Europe/Ljubljana'  # do we need this anywhere? Houses Matrycs

######
# PV #
######
PV_nominal_power = 5000  # in Wp
tiltPV = 35  # PV modules inclination
azimuthPV = 0  # - 90° is East, 0° is South and 90° is West.

########################
# building definitions #
########################
windows_area = 20
walls_area = 500
floor_area = 200.0
volume_building = 414
U_walls = 0.2
U_windows = 1.1
ach_vent = 0.35
ventilation_efficiency = 0.6

# Very light: 80 000 Light: 110 000 Medium: 165 000 Heavy: 260 000 Very heavy:370 000
thermal_capacitance = 165000

t_set = 22.0

# south window definitions
south_window_area = 10
south_window_azimuth = 0
windows_tilt = 90

##########################
# familly house profiles #
##########################
numDays = 1  # number of days, will be always 1 in our case
startDay = 1  # Initial day #only 1 or 2 (1 weekend-holiday / 2 work day ) maybe same as bottom weekend!!!!

#########################################
# Business electric consumption profile #
#########################################
background_consumption = 1000
peak_consumption = 5000
office_start_t = 9 * 60  # minutees
office_end_t = 17 * 60
weekend = False

###########
# battery #
###########
bat_capacity = 10000  # Wh
bat_power = 3000  # W charging discarging power
bat_efficiency = 0.9  # return efficiency of the battery

###################
# heating/cooling #
###################
heating_type = 1  # 1-HVAC, 2-el. heater, 3-other, not used for estimating electric consumption
cooling_type = 1  # 1- air-conditioner, 2-other not used for estimating electric consumption

###########
# EV/PHEV #
###########
EV_capacity = 30000  # [Wh]
EV_power = 3000  # [W] maks charging power
