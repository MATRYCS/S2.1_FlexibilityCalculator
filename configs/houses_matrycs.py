#!/usr/bin/python3    

# Artifical load profile generator v1.1, generation of artificial load profiles to benchmark demand side management approaches
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


# This is an example configuration file!

# Select the output writer
import writer as writer

# Random seed
seed = 42

# Simulation:
# number of days to simulate and skipping of initial days. Simulation starts at Sunday January 1.
numDays = 1  # number of days, will be always 1 in our case
startDay = 1  # Initial day #only 1 or 2 (1 weekend-holiday / 2 work day )

# Select the geographic location. Refer to the Astral plugin to see available locations (or give a lon+lat)
# Use e.g. https://www.latlong.net/
from astral import location

location = location.Location()  # latest astral library version needs location.Location instead location!!!
location.solar_depression = 'civil'
location.latitude = 46.6
location.longitude = 14.4
location.timezone = 'Europe/Ljubljana'
# location.elevation = 300

# Select the devices in the neighbourhood

# Devices
# Scale overall consumption:
consumptionFactor = 1.0  # consumption was a bit too high

# Penetration of emerging technology in percentages
# all values must be between 0-100
# These indicate what percentage of the houses has a certain device

# Electric mobility, restriction that the sum <= 100
# Note, households with larger driving distances will receive EVs first
penetrationEV = 100
penetrationPHEV = 0

# we are using PVGIS therefore it needs to be 0
penetrationPV = 0
penetrationBattery = 0  # Note only houses with PV will receive a battery!

# We are using RC-SIMULATOR therefore 0
penetrationHeatPump = 0
penetrationCHP = 0  # Combined heat and power

penetrationInductioncooking = 25

# Device parameters:
# EV
capacityEV = 420000  # Wh
powerEV = 7400  # W
capacityPHEV = 12000  # Wh
powerPHEV = 3700  # W

# PV not needed!
PVProductionPerYear = 220  # average kWh per m2 solar panel on annual basis
PVAngleMean = 35  # degrees, 0 is horizontal to earth surface
PVAngleSigma = 10  # degrees
PVAzimuthMean = 180  # degrees, 0 is north, 90 is east
PVAzimuthSigma = 90  # degrees
PVEfficiencyMin = 15  # % of theoretical max
PVEfficiencyMax = 20  # % of theoretical max

# Driving distances
commuteDistanceMean = 25  # km
commuteDistanceSigma = 10  # km

# Battery
capacityBatteryLarge = 12000  # Wh
capacityBatteryMedium = 5000  # Wh
capacityBatterySmall = 2000  # Wh
powerBatteryLarge = 3700  # W
powerBatteryMedium = 3700  # W
powerBatterySmall = 3700  # W

# Kitchen
# Consumption of devices
ConsumptionOven = 2000  # W
ConsumptionMicroWave = 800  # W
ConsumptionStoveVentilation = 120  # W #But this is maximum, usually set lower!
ConsumptionInductionStove = 2200  # W #http://homeguides.sfgate.com/many-watts-induction-stove-85380.html

ConsumptionFridgeBigMin = 80  # W
ConsumptionFridgeBigMax = 120  # W
ConsumptionFridgeSmallMin = 50  # W
ConsumptionFridgeSmallMax = 80  # W

ConsumptionKettle = 2000  # W

# White goods
ConsumptionIron = 2000  # W
ConsumptionVacuumcleaner = 1500  # W

# House
ConsumptionHouseVentilation = 50  # W

# Household randomization
# all values must be between 0-1000
familyOutingChanceMin = 10  # percentage
familyOutingChanceMax = 20  # percentage
personWeekdayActivityChanceMin = 20  # percentage
personWeekdayActivityChanceMax = 30  # percentage
personWeekendActivityChanceMin = 20  # percentage
personWeekendActivityChanceMax = 30  # percentage

householdList = []

# Select the types of households
import households

# typical family house
householdList.append(households.HouseholdFamilyDualParent(parttime=False, jobless=False))

