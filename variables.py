#!/usr/bin/python3
# common variables

#get the irradiance data from the website for a specific location and month
m = 2
latitude = 46.056946
longitude = 14.505751
timezone = 'Europe/Ljubljana' #do we need this anywhere?
PV_nominal_power = 5000 # in Wp
tiltPV = 35 #PV modules inclination
azimuthPV = 0 #- 90° is East, 0° is South and 90° is West.
numDays = 1  # number of days, will be always 1 in our case
startDay = 1  # Initial day #only 1 or 2 (1 weekend-holiday / 2 work day )


#building definitions
windows_area = 20
walls_area = 500
floor_area = 200.0
volume_building = 414
U_walls = 0.2
U_windows=1.1
ach_vent=0.35
ventilation_efficiency=0.6

# Very light: 80 000 Light: 110 000 Medium: 165 000 Heavy: 260 000 Very heavy:370 000
thermal_capacitance = 165000

t_set=22.0
#south window definitions
south_window_area = 10
south_window_azimuth = 0
windows_tilt = 90


#Business profile
background_consumption = 1000
peak_consumption = 5000
office_start_t = 9*60 #minutees
office_end_t = 17*60
weekend = False