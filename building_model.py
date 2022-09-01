"""
Building model to calculate the energy equilibrium for the house
Author: Andrej Campa

HOW TO USE

    first initialize the class
    if the floor area is not known and volume, use estimate_parameters function
    define internal gains and solar gains, reset solar gains after each hour,
    function solar_power_gains allows to add more windows
    solve_energy(t_out) #Solve for Heating/Cooling


VARIABLE DEFINITION
    internal_gains: Internal Heat Gains [W]
    solar_gains: Solar Heat Gains after transmitting through the window [W]
    t_out: Outdoor air temperature [C]
    t_m_prev: Thermal mass temperature from the previous time step

INPUT PARAMETER DEFINITION
    window_area: Area of the Glazed Surface on the envelope of the building building [m2]
    walls_area: Area of all envelope surfaces, including windows in contact with the outside
    floor_area : floor area of zone [m2]
    volume_building: volume of interior zone [m3]
    u_walls: U value of facade  [W/m2K]
    u_windows: U value of glazed surfaces of windows [W/m2K]
    air_vent: fraction of air changed per hour through ventilation,
                0.35 means approx. one third of air volume is changed in hour
    ventilation_efficiency: The efficiency of the heat recovery system for ventilation. Set to 0 if there is no heat
        recovery, 1 means heat recovery is 100% effective, no losses from ventilation
    thermal_capacitance_per_floor_area: Thermal capacitance of the room per floor area [J/m2K]
                                        Very light: 80 000
                                        Light: 110 000
                                        Medium: 165 000
                                        Heavy: 260 000
                                        Very heavy:370 000
    t_set : Thermal heating/cooling set point of the rooms [C]
"""
import math
from astral.location import Location, LocationInfo
import datetime

class Building(object):
    '''Sets the parameters of the zone. '''

    def __init__(self,
                 window_area=20.0,
                 walls_area=500.0,
                 floor_area=180.0,
                 volume_building=414,
                 U_walls=0.2,
                 U_windows=1.1,
                 ach_vent=0.35,
                 ventilation_efficiency=0.6,
                 thermal_capacitance_per_floor_area=165000,
                 t_set=22.0,
                 ):
        self.window_area = window_area  # [m2] Window Area
        self.walls_area = walls_area
        self.floor_area = floor_area
        self.volume_building = volume_building
        self.U_walls = U_walls
        self.U_windows = U_windows
        self.ach_vent = ach_vent
        self.ventilation_efficiency = ventilation_efficiency
        self.thermal_capacitance_per_floor_area = thermal_capacitance_per_floor_area
        self.t_set = t_set
        self.solar_gains = 0.0
        self.internal_gains = 0.0
        self.heat_demand = 0.0
        self.angle_incidence = 0.0
        self.transmittance = 1.0

    def estimate_parameters(self):
        """
        Estimate volume of the building and floor area from walls area, if they are not known
        """

        # estimate dimension a of the cube from surface area = 6*a^2
        a = (self.walls_area / 6.0) ** 0.5
        no_of_floors = int(a / 3)
        if no_of_floors < 1:
            no_of_floors = 1
        height_of_building = no_of_floors * 3
        # find new a
        a = (-4 * height_of_building + ((4 * height_of_building) ** 2 + 8 * self.walls_area) ** 0.5) / 4
        self.floor_area = no_of_floors * a ** 2
        self.volume_building = self.floor_area * 2.3

    def solar_power_gains(self, window_area, irradiance_dir, irradiance_dif, month, hour=0, tilt=90.0, azimuth=0, transmittance=0.7, lat=45.1, lon=14.1):
        # need to reset solar gains
        self.get_angle(month, hour, lat, lon, tilt, azimuth)
        print(self.angle_incidence)
        self.transmittance_glass(self.angle_incidence)
        self.solar_gains += window_area * (irradiance_dir*self.transmittance + irradiance_dif*(1.0 + math.cos(tilt/180*3.14)) / 2.0) * transmittance

    def calc_heat_demand(self, t_out_air):
        # if the number is positive we need to supply the energy
        # in case of negative number we need to cool down the building
        energy_transition_envelope = (self.U_walls * self.walls_area + self.U_windows * self.window_area) * \
                                     (self.t_set - t_out_air)
        # air heat capacity 700 J/(Kg*K), density of air at 20 degrees at 101.325 kPa is 1204 kg/m3
        # the constants changes with pressure and temperature, but the first estimation is good enough
        air_mass = 1.204 * self.volume_building
        energy_air_vent = 700/(60*60) * air_mass * (self.t_set - t_out_air) * self.ach_vent *\
                          (1.0 - self.ventilation_efficiency)
        self.heat_demand = energy_transition_envelope + energy_air_vent - self.solar_gains - self.internal_gains

    def get_angle(self,month,hour,lat,lon, tilt, azimuth_glazing):
        # get angle between sun and glazing
        # hour in 15 minutees from 0 to 96
        azimuth_glazing += 180 # rotate for 180 degrees to be compliant with astral package S=180
        l = LocationInfo('name', 'region', 'UTC', lat, lon)
        d1 = datetime.datetime(2022,month,15,int(hour/4),15*(hour%4))
        solar_azimuth = Location(l).solar_azimuth(d1)
        solar_height = Location(l).solar_elevation(d1)
        if solar_height < 1: # bellow horizon
            self.angle_incidence = 90
            return
        delta_azimuth = abs(solar_azimuth - azimuth_glazing)
        if abs(delta_azimuth>90): # on the other side
            self.angle_incidence = 90
            return
        faktor=math.sin(math.radians(180 - solar_height - tilt))*math.cos(math.radians(delta_azimuth))
        self.angle_incidence=math.degrees(math.acos(faktor))

    def transmittance_glass(self,angle):
        # angle degrees
        if angle>90:
            self.transmittance = 0.0
            return
        if angle<0:
            self.transmittance = 0.0
            return
        self.transmittance = 1.0 - 0.0401 - 1.178e-4*math.exp(angle*9.987e-2)
