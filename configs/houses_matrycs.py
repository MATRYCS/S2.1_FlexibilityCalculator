#!/usr/bin/python3    
# Author: Andrej Campa
# This is the file that execute statistic based profile generation of households. Different types of households
# are available according to the ALPG library
# Additional options to modify asset penetration is available here.
import sys

# Select the output writer
sys.path.append('./alpg')
import writer as writer
# Select the geographic location. Refer to the Astral plugin to see available locations (or give a lon+lat)
# Use e.g. https://www.latlong.net/
from astral import location
import households


class House_types(object):
    def __init__(self,
                 startDay=1,
                 latitude=46.6,
                 longitude=14.4,
                 timezone='Europe/Ljubljana'
                 ):
        self.startDay = startDay  # Initial day #only 1 or 2 (1 weekend-holiday / 2 work day )
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.householdList = []
        # Devices

        # Select the devices in the neighbourhood

        # Penetration of emerging technology in percentages
        # all values must be between 0-100
        # These indicate what percentage of the houses has a certain device

        # Electric mobility, restriction that the sum <= 100
        # Note, households with larger driving distances will receive EVs first
        self.penetrationEV = 100
        self.penetrationPHEV = 0

        # we are using PVGIS therefore it needs to be 0
        self.penetrationPV = 0
        self.penetrationBattery = 0  # Note only houses with PV will receive a battery!

        # We are using RC-SIMULATOR therefore 0
        self.penetrationHeatPump = 0
        self.penetrationCHP = 0  # Combined heat and power

        self.penetrationInductioncooking = 25

        # Device parameters:
        # EV
        self.capacityEV = 420000  # Wh
        self.powerEV = 7400  # W
        self.capacityPHEV = 12000  # Wh
        self.powerPHEV = 3700  # W

    def calculation(self, house_type):
        location1 = location.Location()  # latest astral library version needs location.Location instead location!!!
        location1.solar_depression = 'civil'
        location1.latitude = self.latitude
        location1.longitude = self.longitude
        location1.timezone = self.timezone
        self.householdList = []
        # Select the types of households
        # typical family house
        print(house_type)
        # types_of_family = ["Single worker", "Single jobless", "Single part-time", "Couple", "Dual worker", "Family dual parent", "Family dual worker", "Family single parent", "Dual retired", "Single retired"]
        if house_type == "Single worker":
            self.householdList.append(households.HouseholdSingleWorker())
        elif house_type == "Single jobless":
            self.householdList.append(households.HouseholdSingleJobless())
        elif house_type == "Single part-time":
            self.householdList.append(households.HouseholdSingleParttime())
        elif house_type == "Couple":
            self.householdList.append(households.HouseholdCouple())
        elif house_type == "Dual worker":
            self.householdList.append(households.HouseholdDualWorker())
        elif house_type == "Family dual parent":
            self.householdList.append(households.HouseholdFamilyDualParent(parttime=False, jobless=False, startDay=self.startDay))
        elif house_type == "Family dual worker":
            self.householdList.append(households.HouseholdFamilyDualWorker())
        elif house_type == "Family single parent":
            self.householdList.append(households.HouseholdFamilySingleParent())
        elif house_type == "Dual retired":
            self.householdList.append(households.HouseholdDualRetired())
        else:  # "Single retired"
            self.householdList.append(households.HouseholdSingleRetired())
