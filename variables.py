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
