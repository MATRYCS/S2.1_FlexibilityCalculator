# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 07:44:06 2022

@authors: Andrej Campa, Denis Sodin

TODO: EV penetration
"""
import random
import json

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import profilegenerator2
import altair as alt

com_build_on = False
number_of_cars = 1
distance_EV = 0
created_profiles_bool = False


def save_values(value):
    """
    Function that saves the state on each parameter change!
    :param value: the changed value
    :type value: string
    :return: none
    :rtype: none
    """
    # save state parameters!
    progress_bar.progress(0)
    progress_bar_PV.progress(0)
    if value == 'radio_BH':
        st.session_state.df.loc[st.session_state.building_no,'type_building'] = st.session_state.radio_BH
    elif value == 'type_of_family':
        st.session_state.df.loc[st.session_state.building_no, 'type_of_family'] = st.session_state.family
    elif value == 'heating_type':
        st.session_state.df.loc[st.session_state.building_no, 'heating_type'] = st.session_state.heating_type
    elif value == 'cooling_type':
        st.session_state.df.loc[st.session_state.building_no, 'cooling_type'] = st.session_state.cooling_type
    elif value == 'heating_P':
        st.session_state.df.loc[st.session_state.building_no, 'heating_el_P'] = st.session_state.heating_P
    elif value == 'cooling_P':
        st.session_state.df.loc[st.session_state.building_no, 'cooling_el_P'] = st.session_state.cooling_P
    elif value == 'background_P':
        st.session_state.df.loc[st.session_state.building_no, 'background_P'] = st.session_state.background_P
    elif value == 'peak_P':
        st.session_state.df.loc[st.session_state.building_no, 'peak_P'] = st.session_state.peak_P
    elif value == 'office_start':
        st.session_state.df.loc[st.session_state.building_no, 'office_start'] = st.session_state.office_start
    elif value == 'office_end':
        st.session_state.df.loc[st.session_state.building_no, 'office_end'] = st.session_state.office_end
    elif value == 'room_param':
        st.session_state.df.loc[st.session_state.building_no, 'room_param'] = st.session_state.room_param
    elif value == 'walls':
        st.session_state.df.loc[st.session_state.building_no, 'walls'] = st.session_state.walls
    elif value == 'U_walls':
        st.session_state.df.loc[st.session_state.building_no, 'U_walls'] = st.session_state.U_walls
    elif value == 'T_set':
        st.session_state.df.loc[st.session_state.building_no, 'T_set'] = st.session_state.T_set
    elif value == 'floor_area':
        st.session_state.df.loc[st.session_state.building_no, 'floor_area'] = st.session_state.floor_area
    elif value == 'volume_building':
        st.session_state.df.loc[st.session_state.building_no, 'volume_building'] = st.session_state.volume_building
    elif value == 'ach_vent':
        st.session_state.df.loc[st.session_state.building_no, 'ach_vent'] = st.session_state.ach_vent
    elif value == 'vent_eff':
        st.session_state.df.loc[st.session_state.building_no, 'vent_eff'] = st.session_state.vent_eff
    elif value == 'thermal_cap':
        st.session_state.df.loc[st.session_state.building_no, 'thermal_cap'] = st.session_state.thermal_cap
    elif value == 'window_param':
        st.session_state.df.loc[st.session_state.building_no, 'window_param'] = st.session_state.window_param
    elif value == 'window_area':
        st.session_state.df.loc[st.session_state.building_no, 'window_area'] = st.session_state.window_area
    elif value == 'U_window':
        st.session_state.df.loc[st.session_state.building_no, 'U_window'] = st.session_state.U_window
    elif value == 'south_window_area':
        st.session_state.df.loc[st.session_state.building_no, 'south_window_area'] = st.session_state.south_window_area
    elif value == 'south_window_azimuth':
        st.session_state.df.loc[st.session_state.building_no, 'south_window_azimuth'] = st.session_state.south_window_azimuth
    elif value == 'windows_tilt':
        st.session_state.df.loc[st.session_state.building_no, 'windows_tilt'] = st.session_state.windows_tilt
    #print("Saving state:", st.session_state.df)

def df_change():
    if len(st.session_state.df)+1 > st.session_state.number_buildings:
        list_drop=np.arange(st.session_state.number_buildings + 1,st.session_state.df.index.max()+1)
        #print(list_drop)
        st.session_state.df = st.session_state.df.drop(list_drop)

def df_PV_change():
    if len(st.session_state.df_PV)+1 > st.session_state.number_PV:
        list_drop=np.arange(st.session_state.number_PV + 1,st.session_state.df_PV.index.max()+1)
        #print(list_drop)
        st.session_state.df_PV = st.session_state.df_PV.drop(list_drop)

def save_values_PV(value):
    """
    Function that saves the state on each parameter change!
    :param value: the changed value
    :type value: string
    :return: none
    :rtype: none
    """
    # save state parameters!
    progress_bar.progress(0)
    progress_bar_PV.progress(0)
    if value == 'Pn':
        st.session_state.df_PV.loc[st.session_state.PV_no,'Pn'] = st.session_state.Pn
    elif value == 'Inclination':
        st.session_state.df_PV.loc[st.session_state.PV_no, 'Inclination'] = st.session_state.Inclination
    elif value == 'Azimuth':
        st.session_state.df_PV.loc[st.session_state.PV_no, 'Azimuth'] = st.session_state.Azimuth
    #print("Saving state:", st.session_state.df_PV)

def up_file():
    """
    function to create state for file upload
    :return: refreshed state
    :rtype: int
    """
    st.session_state.file_state=1

# define all possible states
# dataframe for storing houses types, building envelope parameters and HVAC details
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns={'type_building': pd.Series(dtype='str'),
                                                'type_of_family': pd.Series(dtype='str'),
                                                'cooling_type': pd.Series(dtype='str'),
                                                'cooling_el_P': pd.Series(dtype='int'),
                                                'heating_type': pd.Series(dtype='str'),
                                                'heating_el_P': pd.Series(dtype='int'),
                                                'background_P': pd.Series(dtype='int'),
                                                'peak_P': pd.Series(dtype='int'),
                                                'office_start': pd.Series(dtype='int'),
                                                'office_end': pd.Series(dtype='int'),
                                                'room_param': pd.Series(dtype='str'),
                                                'walls': pd.Series(dtype='int'),
                                                'U_walls': pd.Series(dtype='float'),
                                                'T_set': pd.Series(dtype='int'),
                                                'floor_area': pd.Series(dtype='int'),
                                                'volume_building': pd.Series(dtype='int'),
                                                'ach_vent': pd.Series(dtype='float'),
                                                'vent_eff': pd.Series(dtype='float'),
                                                'thermal_cap': pd.Series(dtype='int'),
                                                'window_param': pd.Series(dtype='str'),
                                                'window_area': pd.Series(dtype='int'),
                                                'U_window': pd.Series(dtype='float'),
                                                'south_window_area': pd.Series(dtype='int'),
                                                'south_window_azimuth': pd.Series(dtype='int'),
                                                'windows_tilt': pd.Series(dtype='int'),
                                                },
    )
    # initialize all values
    st.session_state.df.loc[1] = ['private house', 'Single worker',  'Air conditioner', 3000,  'Heat pump', 2000,
                                  1000, 5000, 9, 17, 'Basic',  500, 0.2, 20, 500, 400, 0.35, 0.6, 165000,
                                  'Basic', 20, 1.1, 10, 0, 90]
    st.session_state.radio_BH = 'private house'
    st.session_state.family = 'Single worker'
    st.session_state.cooling_type = 'Air conditioner'
    st.session_state.cooling_P = 2000
    st.session_state.heating_type = 'Heat pump'
    st.session_state.heating_P = 3000
    st.session_state.background_P = 1000
    st.session_state.peak_P = 5000
    st.session_state.room_param = 'Basic'
    st.session_state.office_start = 9
    st.session_state.office_end = 17
    st.session_state.T_set = 20
    st.session_state.floor_area = 500
    st.session_state.volume_building = 400
    st.session_state.ach_vent = 0.35
    st.session_state.vent_eff = 0.6
    st.session_state.thermal_cap = 165000
    st.session_state.window_param = 'Basic'
    st.session_state.window_area = 20
    st.session_state.U_window = 1.1
    st.session_state.south_window_area = 10
    st.session_state.south_window_azimuth = 0
    st.session_state.windows_tilt = 90
    st.session_state.EV_capacity = 40.00
    st.session_state.EV_power = 3.7
    st.session_state.penetration_EV = 50
    st.session_state.commute_distance_EV = 25
    st.session_state.number_of_cars = 1
    st.session_state.distance_EV = 20
    st.session_state.bat_capacity = 15.0
    st.session_state.bat_power = 5.0
    st.session_state.bat_efficiency = 90.0
    st.session_state.latitude = 46.050
    st.session_state.longitude = 14.510

if 'df_PV' not in st.session_state:
    st.session_state.df_PV = pd.DataFrame(columns={'Pn': pd.Series(dtype='float'),
                                                'Inclination': pd.Series(dtype='int'),
                                                'Azimuth': pd.Series(dtype='float'),
                                                },
    )
    st.session_state.df_PV.loc[1]=[5.0,30,0.0]
    st.session_state.Pn = 5.0
    st.session_state.Inclination = 30
    st.session_state.Azimuth = 0

if 'file_state' not in st.session_state:
    st.session_state.file_state = 0

use_case = profilegenerator2.profilgenerator2()

st.sidebar.write("**Project**")

# create one JSON object before saving!
save_button = st.sidebar.download_button('Save project',
                                         data=json.dumps({'df': st.session_state.df.to_dict(),
                                                          'df_PV': st.session_state.df_PV.to_dict(),
                                                          'EV_capacity': st.session_state.EV_capacity,
                                                          'EV_power': st.session_state.EV_power,
                                                          'penetration_EV': st.session_state.penetration_EV,
                                                          'commute_distance_EV': st.session_state.commute_distance_EV,
                                                          'number_of_cars':st.session_state.number_of_cars,
                                                          'distance_EV':st.session_state.distance_EV,
                                                          'bat_capacity':st.session_state.bat_capacity,
                                                          'bat_power':st.session_state.bat_power,
                                                          'bat_efficiency':st.session_state.bat_efficiency,
                                                          'latitude':st.session_state.latitude,
                                                          'longitude':st.session_state.longitude
                                                          }
                                                         ))

uploaded_file = st.sidebar.file_uploader("Open project",on_change=up_file)
if uploaded_file is not None and st.session_state.file_state == 1:
    dataobj = json.load(uploaded_file)
    dataframe_from_dict = pd.DataFrame.from_dict(dataobj['df']).astype({'type_building':str,
                                                'type_of_family': str,
                                                'cooling_type': str,
                                                'cooling_el_P': int,
                                                'heating_type': str,
                                                'heating_el_P': int,
                                                'background_P': int,
                                                'peak_P': int,
                                                'office_start': int,
                                                'office_end': int,
                                                'room_param': str,
                                                'walls': int,
                                                'U_walls': float,
                                                'T_set': int,
                                                'floor_area': int,
                                                'volume_building':int,
                                                'ach_vent': float,
                                                'vent_eff': float,
                                                'thermal_cap': int,
                                                'window_param': str,
                                                'window_area': int,
                                                'U_window': float,
                                                'south_window_area': int,
                                                'south_window_azimuth': int,
                                                'windows_tilt': int})
    dataframe_from_dict.index = dataframe_from_dict.index.astype('int64')
    st.session_state.df = dataframe_from_dict
    dataframe_from_dict = pd.DataFrame.from_dict(dataobj['df_PV']).astype({'Pn': float,
                                                                        'Inclination': int,
                                                                           'Azimuth':float
                                                                        })
    dataframe_from_dict.index = dataframe_from_dict.index.astype('int64')
    st.session_state.df_PV = dataframe_from_dict
    st.session_state.number_buildings = len(st.session_state.df)
    st.session_state.number_PV = len(st.session_state.df_PV)
    st.session_state.EV_capacity = float(dataobj['EV_capacity'])
    st.session_state.EV_power = float(dataobj['EV_power'])
    st.session_state.penetration_EV = int(dataobj['penetration_EV'])
    st.session_state.commute_distance_EV = int(dataobj['commute_distance_EV'])
    st.session_state.number_of_cars = int(dataobj['number_of_cars'])
    st.session_state.distance_EV = int(dataobj['distance_EV'])
    st.session_state.bat_capacity = float(dataobj['bat_capacity'])
    st.session_state.bat_power = float(dataobj['bat_power'])
    st.session_state.bat_efficiency = float(dataobj['bat_efficiency'])
    st.session_state.latitude = float(dataobj['latitude'])
    st.session_state.longitude = float(dataobj['longitude'])
    st.session_state.file_state = 0

st.sidebar.write("**General parameters**")
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
month = st.sidebar.selectbox("Month of the year", months, key="month")
use_case.month = months.index(month) + 1
types_of_day = ["Workday", "Weekend/Holiday"]
type_of_day = st.sidebar.selectbox("Day of the week", types_of_day, key='weekend')
use_case.weekend = types_of_day.index(type_of_day)
use_case.latitude = st.sidebar.number_input("Latitude [°]", min_value=-90.0, max_value=90.0, format="%.4f",
                                            help="Geographical latitude", step = 0.0001, key='latitude')
use_case.longitude = st.sidebar.number_input("Longitude [°]", min_value=-180.0, max_value=180.0,
                                             format="%.4f", step = 0.0001, key='longitude',
                                             help="Geographical longitude")

data = np.array([[use_case.latitude, use_case.longitude]])

map_data = pd.DataFrame(data, columns=["lat", "lon"])

st.title("Matrycs - Catalogue service")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    ["🗺️Map", "📃Zone", "📃PV", "📃EV", "📃Battery", "📈Profiles", "📊Flexibility", "🔌Substation", "📓Data"])
with tab1:
    st.map(map_data)

with tab2:
    col1, col2, = st.columns(2)
    with col2:
        # due to race condition, reading at the end of file...
        st.number_input("Maximum number of buildings in zones", min_value=1, max_value=None, value=1,
                        key='number_buildings', help="Specify the number of buildings in the zone.",
                                                     on_change=df_change)
    with col1:
        st.session_state.building_no = st.number_input("Selected building",
                                       min_value=1, max_value=st.session_state.number_buildings, value=1,
                                       help="Used to scroll through individual building perameters.")
    # initialize all values
    if st.session_state.building_no not in st.session_state.df.index:
        st.session_state.df.loc[st.session_state.building_no] = ['private house', 'Single worker', 'Air conditioner', 3000, 'Heat pump', 2000,
                                                                    1000, 5000, 9, 17, 'Basic', 500, 0.2, 20, 500, 400, 0.35, 0.6, 165000,
                                                                 'Basic', 20, 1.1, 10, 0, 90]
    b_types = ['private house', 'commercial building']
    # for a proper refreshing you have to change the state of the radio button before you call it!
    # also the variable must be defined first before you call it! During the creation of the radio button
    # the [key] parameter is matched with st.session_state.[key]!!!
    # Do not try to change the [key] during the callback!!! It will not work as it should!!!!
    st.session_state.radio_BH = st.session_state.df.loc[st.session_state.building_no, "type_building"]
    com_build_on = st.radio('Select type of the building', b_types, key="radio_BH",on_change=save_values, args =("radio_BH",))
    st.write("----------------------------------------------------------------------------------")
    types_of_family = ["Single worker", "Single jobless", "Single part-time", "Couple", "Dual worker",
                       "Family dual parent", "Family dual worker", "Family single parent", "Dual retired",
                       "Single retired"]
    if com_build_on == 'private house':
        st.write("**Household parameters**")
        st.session_state.family = st.session_state.df.loc[st.session_state.building_no, "type_of_family"]
        st.selectbox("Type of household", types_of_family, key='family', on_change=save_values, args =("type_of_family",))

    else:
        st.write("**Commercial**")
        st.session_state.background_P = st.session_state.df.loc[st.session_state.building_no, "background_P"]
        use_case.background_consumption = st.number_input("Background power [W]", min_value=0, max_value=None,
                                                          value=1000, key='background_P', on_change=save_values, args =("background_P",),
                                                          help="Consumption of all appliances in the building that can not be turned off [W].")
        st.session_state.peak_P = st.session_state.df.loc[st.session_state.building_no, "peak_P"]
        use_case.peak_consumption = st.number_input("Peak power [W]", min_value=0, max_value=None, value=5000,
                                                    key='peak_P', on_change=save_values, args=("peak_P",),
                                                    help="Peak consumption when all employees are present in their workplace [W].")
        start_hours = [5, 6, 7, 8, 9, 10, 11]
        end_hours = [13, 14, 15, 16, 17, 18, 19]
        st.session_state.office_start = st.session_state.df.loc[st.session_state.building_no, "office_start"]
        use_case.office_start_t = st.selectbox("Starting hour of workday", start_hours, index=4, key='office_start', on_change=save_values, args =("office_start",)) * 60
        st.session_state.office_end = st.session_state.df.loc[st.session_state.building_no, "office_end"]
        use_case.office_end_t = st.selectbox("Ending hour of workday", end_hours, index=4,key='office_end', on_change=save_values, args =("office_end",) ) * 60
    st.write("----------------------------------------------------------------------------------")
    st.write("**Heating / cooling parameters**")
    heat_types = ["Heat pump", "Electric heater", "Other"]
    cool_types = ["Air conditioner", "Other"]

    col1, col2, = st.columns(2)
    with col1:
        st.session_state.heating_type = st.session_state.df.loc[st.session_state.building_no, "heating_type"]
        heating_type = st.selectbox("Type of heating", heat_types, key='heating_type', on_change=save_values, args =("heating_type",) )

    with col2:
        st.session_state.cooling_type = st.session_state.df.loc[st.session_state.building_no, "cooling_type"]
        cooling_type = st.selectbox("Type of cooling", cool_types, key='cooling_type', on_change=save_values, args =("cooling_type",))

    use_case.heating_type = heat_types.index(heating_type) + 1
    use_case.cooling_type = cool_types.index(cooling_type) + 1

    col1, col2, = st.columns(2)
    with col1:
        st.session_state.heating_P = st.session_state.df.loc[st.session_state.building_no, "heating_el_P"]
        use_case.heating_el_P = st.number_input("Max electrical power of heating device [W]",
                                       min_value=0, max_value=None, value=3000, key='heating_P', on_change=save_values, args =("heating_P",),
                                       help="This is the el. power of the device in the case of HVAC, the COP "
                                            "(Coefficient Of Performance) number will increase the heating power of HVAC")

    with col2:
        st.session_state.cooling_P = st.session_state.df.loc[st.session_state.building_no, "cooling_el_P"]
        use_case.cooling_el_P = st.number_input("Max electrical power of cooling device [W]",
                                       min_value=0, max_value=None, value=2000, key='cooling_P', on_change=save_values, args =("cooling_P",),
                                       help="This is the el. power of the device in case of air conditioning, the COP "
                                            "(Coefficient Of Performance) number will increase the cooling power")
    st.write("----------------------------------------------------------------------------------")

    st.write("**Rooms parameters**")
    st.session_state.room_param = st.session_state.df.loc[st.session_state.building_no, "room_param"]
    room_param = st.radio("Type of known rooms parameters", ["Basic", "Advanced"],
                          key='room_param', on_change=save_values, args=("room_param",),
                          help="When basic option is selected some of the parameters will be automatically generated as typicall values. Choose advanced option if all parameters are known.")
    col5, col6 = st.columns(2)
    with col5:
        st.session_state.walls = st.session_state.df.loc[st.session_state.building_no, "walls"]
        use_case.walls_area = st.number_input("Walls area [m²]", min_value=0, max_value=None, value=400,
                                              key='walls', on_change=save_values, args =("walls",),
                                              help="Area of all envelope surfaces, including windows in contact with the outside.")

    with col6:
        st.session_state.U_walls = st.session_state.df.loc[st.session_state.building_no, "U_walls"]
        use_case.U_walls = st.number_input("U value of facade [W/m²K]", min_value=0.0, max_value=None, value=0.2,
                                           key='U_walls', on_change=save_values, args =("U_walls",),)
    st.session_state.T_set = st.session_state.df.loc[st.session_state.building_no, "T_set"]
    use_case.t_set = st.number_input("Room temperature [°]", min_value=15, max_value=30, value=20,
                                     key='T_set', on_change=save_values, args=("T_set",),
                                     help="Set the desired room temperature.")

    if room_param == "Basic":
        """
        Estimate volume of the building and floor area from walls area, if they are not known
        """
        # estimate dimension a of the cube from surface area = 6*a^2
        a = (use_case.walls_area / 6.0) ** 0.5
        no_of_floors = int(a / 3)
        if no_of_floors < 1:
            no_of_floors = 1
        height_of_building = no_of_floors * 3
        # find new a
        a = (-4 * height_of_building + ((4 * height_of_building) ** 2 + 8 * use_case.walls_area) ** 0.5) / 4
        use_case.floor_area = no_of_floors * a ** 2
        use_case.volume_building = use_case.floor_area * 2.3

        st.write("Estimated floor area from walls area is:", use_case.floor_area)
        st.write("Estimated building volume from walls area is:", use_case.volume_building)
        use_case.ach_vent = 0.35
        st.write("Fraction of air mass exchanged through ventilation. Currently selected value is:", use_case.ach_vent)
        use_case.ventilation_efficiency = 0.6
        st.write(
            "The efficiency of the heat recovery system for ventilation: 0 if there is no heat recovery, 1 if heat recovery is 100% effective. Currently selected value is:",
            use_case.ach_vent)
        use_case.thermal_capacitance = 165000
        st.write("Thermal capacitance of the room [J/m²K]. Currently selected value is:", use_case.thermal_capacitance)

    if room_param == "Advanced":
        st.session_state.floor_area = st.session_state.df.loc[st.session_state.building_no, "floor_area"]
        use_case.floor_area = st.number_input("Floor area [m²]", min_value=0, max_value=None, value=500,
                                              key='floor_area', on_change=save_values, args=("floor_area",),)
        st.session_state.volume_building = st.session_state.df.loc[st.session_state.building_no, "volume_building"]
        use_case.volume_building = st.number_input("Building volume [m³]", min_value=0, max_value=None, value=400,
                                                   key='volume_building', on_change=save_values, args=("volume_building",),)
        st.session_state.ach_vent = st.session_state.df.loc[st.session_state.building_no, "ach_vent"]
        use_case.ach_vent = st.number_input("Fraction of air mass exchanged through ventilation", min_value=0.0,
                                            max_value=1.0, value=0.35, key='ach_vent', on_change=save_values, args=("ach_vent",),
                                            help="Fraction of air changed per hour through ventilation, 0.35 means approx. one third of air volume is changed in a hour.")
        st.session_state.vent_eff = st.session_state.df.loc[st.session_state.building_no, "vent_eff"]
        use_case.ventilation_efficiency = st.number_input("Ventilation efficiency", min_value=0.0, max_value=1.0,
                                                          value=0.6, key='vent_eff', on_change=save_values, args=("vent_eff",),
                                                          help="The efficiency of the heat recovery system for ventilation. Set to 0 if there is no heat recovery, 1 means heat recovery is 100% effective, no losses from ventilation.")
        thermal_capacitances = [80000, 110000, 165000, 260000, 370000]
        st.session_state.thermal_cap = st.session_state.df.loc[st.session_state.building_no, "thermal_cap"]
        use_case.thermal_capacitance = st.selectbox("Thermal capacitance [J/m²K]", thermal_capacitances,
                                                    key='thermal_cap', on_change=save_values, args=("thermal_cap",),
                                                    help="Thermal capacitance of the room. Very light: 80 000, Light: 110 000,  Medium: 165 000, Heavy: 260 000, Very heavy: 370 000",
                                                    index=2)

    st.write("----------------------------------------------------------------------------------")
    st.write("**Windows parameters**")
    st.session_state.window_param = st.session_state.df.loc[st.session_state.building_no, "window_param"]
    win_param = st.radio("Type of known windows parameters", ["Basic", "Advanced"],
                         key='window_param', on_change=save_values, args=("window_param",),
                         help="When basic option is selected some of the parameters will be automatically generated as typicall values. Choose advanced option if all parameters are known.")
    col3, col4 = st.columns(2)
    with col3:
        st.session_state.window_area = st.session_state.df.loc[st.session_state.building_no, "window_area"]
        use_case.window_area = st.number_input("Window area [m²]", min_value=0, max_value=None, value=20,
                                               key='window_area', on_change=save_values, args=("window_area",),
                                               help="Area of the Glazed Surface in contact with the outside.")

    with col4:
        st.session_state.U_window = st.session_state.df.loc[st.session_state.building_no, "U_window"]
        use_case.U_window = st.number_input("U value of glazed surfaces of windows [W/m²K]", min_value=0.0,
                                             key='U_window', on_change=save_values, args=("U_window",),
                                             max_value=None, value=1.1)

    if win_param == "Basic":
        st.write("Assumed value of south window area is 1/3 of entire window area. Current south window area =",
                 round(use_case.window_area / 3, 2), "[m²].")
        use_case.south_window_area /= 3
        use_case.south_window_azimuth = 0
        st.write(
            "Azimuth of windows is the angle of the windows relative to the direction due South [- 90° is East, 0° is South and 90° is West.]. Currently assumed orientation of windows is:",
            use_case.south_window_azimuth, "°.")
        use_case.windows_tilt = 90
        st.write("Inclination slope is the angle of the windows from the horizontal plane. Currently assumed value is:",
                 use_case.windows_tilt, "°.")

    if win_param == "Advanced":
        st.session_state.south_window_area = st.session_state.df.loc[st.session_state.building_no, "south_window_area"]
        use_case.south_window_area = st.number_input("South window area [m²]", min_value=0, max_value=None, value=10,
                                                     key='south_window_area', on_change=save_values, args=("south_window_area",),
                                                     help="Area of windows facing the south.")
        st.session_state.south_window_azimuth = st.session_state.df.loc[st.session_state.building_no, "south_window_azimuth"]
        use_case.south_window_azimuth = st.number_input("Azimuth of south windows [°]", min_value=-90, max_value=90,
                                                        value=0, key='south_window_azimuth', on_change=save_values, args=("south_window_azimuth",),
                                                        help="The azimuth, or orientation, is the angle of the windows relative to the direction due South. - 90° is East, 0° is South and 90° is West.")
        st.session_state.windows_tilt = st.session_state.df.loc[st.session_state.building_no, "windows_tilt"]
        use_case.windows_tilt = st.number_input("Inclination/slope [°]", min_value=0, max_value=90, value=90,
                                                key='windows_tilt', on_change=save_values, args=("windows_tilt",),
                                                help="Angle of the south windows from the horizontal plane")

with tab3:
    col1, col2, = st.columns(2)
    with col2:
        st.number_input("Number of PV systems",
                                       min_value=1, max_value=None, value=1, key='number_PV', on_change=df_PV_change,
                                       help="Specify number of different PV systems. For your convenience, you can "
                                            "divide a system with different orientations into several systems. On the "
                                            "other hand, you can also merge parts of different systems with the same "
                                            "orientation.")
    with col1:
        st.session_state.PV_no = st.number_input("Selected PV plant",
                                       min_value=1, max_value=st.session_state.number_PV, value=1,
                                       help="Used to scroll through individual PV systems perameters.")

        # initialize all values
    if st.session_state.PV_no not in st.session_state.df_PV.index:
        st.session_state.df_PV.loc[st.session_state.PV_no] = [5.0,30,0.0]

    st.header("Parameters")
    st.session_state.Pn = st.session_state.df_PV.loc[st.session_state.PV_no,"Pn"]
    use_case.PV_nominal_power = st.number_input("Installed peak power of the PV [kWp]", min_value=0.0, key='Pn',
                                                max_value=None, value=5.0, format=None, on_change=save_values_PV, args=("Pn",),) * 1000

    st.session_state.Inclination =  st.session_state.df_PV.loc[st.session_state.PV_no,"Inclination"]
    use_case.tiltPV = st.number_input("Inclination/slope [°]", min_value=0, max_value=90, value=30, format=None, key='Inclination',
                                      help="Angle of the PV modules from the horizontal plane",
                                         on_change=save_values_PV, args=("Inclination",))
    st.session_state.Azimuth = st.session_state.df_PV.loc[st.session_state.PV_no, "Azimuth"]
    use_case.azimuthPV = st.number_input("Azimuth [°]", min_value=-180.0, max_value=180.0, value=0.0, step=0.1,
                                         format=None, key='Azimuth', on_change=save_values_PV, args=("Azimuth",),
                                             help="The azimuth, or orientation, is the angle of the PV modules relative to the direction due South. - 90° is East, 0° is South and 90° is West.")

with tab4:
    st.write("**Typical EV characteristic in zone**")
    use_case.EV_capacity = st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None,
                                           value=40.0, key='EV_capacity',
                                           help="The battery must be large enough to cover the entire commute. Otherwise, depending on the size of the battery, only part of the distance will be considered!") * 1000
    use_case.EV_power = st.number_input("Charging power [kW]", min_value=0.0, max_value=None, value=3.7, key='EV_power') * 1000
    st.write("----------------------------------------------------------------------------------")
    st.write("**Households settings**")
    penetration_EV = st.number_input("Penetration of EVs into housholds [%]", min_value=0, max_value=100,
                                           value=50,key='penetration_EV')
    commute_distance_EV = st.number_input("Average one-way commute distance done by EV [km]", min_value=0, max_value=None,
                                  value=25, key='commute_distance_EV',
                                  help="Average daily distance of EV vehicles, you can estimate the total distance divided by the number of vehicles")

    st.write("----------------------------------------------------------------------------------")
    st.write("**Commercial fleet**")
    number_of_cars = st.number_input("Number of vehicles:", min_value=0, max_value=None, value=1,
                                     help="Total number of all EV vehicles in the fleet.", key='number_of_cars')
    distance_EV = st.number_input("Average daily distance done by vehicle [km]", min_value=0, max_value=None,
                                  value=20, key='distance_EV',
                                  help="Average daily distance of EV vehicles, you can estimate the total distance divided by the number of vehicles")

with tab5:

    use_case.bat_capacity = st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=15.0,
                                            step=0.1, key='bat_capacity')
    use_case.bat_power = st.number_input("Peak (dis)charging power [kW]", min_value=0.0, max_value=None, value=5.0,
                                         step=0.1, key='bat_power')
    use_case.bat_efficiency = st.number_input("Charging efficiency [%]", min_value=0.0, max_value=100.0, value=90.0,
                                                  help="Efficiency of battery charging/discharging.", key='bat_efficiency') / 100


run_button = st.sidebar.button('Calculate profiles')
st.sidebar.write("Buildings:")
progress_bar = st.sidebar.progress(0)
st.sidebar.write("PVs:")
progress_bar_PV = st.sidebar.progress(0)
if run_button:
    building = st.session_state.number_buildings
    st.session_state.AC_kWh = 0
    st.session_state.HVAC_kWh = 0
    st.session_state.energies_heating = 0
    st.session_state.energies_cooling = 0
    st.session_state.EV_kWh_dom_flex = 0
    if len(st.session_state.df) >= building:
        for i in range(1,building+1):
            # load all parameters relevant for specific house
            use_case.com_build_on = st.session_state.df.loc[i, "type_building"]
            #print("type", use_case.com_build_on)
            use_case.house_type=st.session_state.df.loc[i, "type_of_family"]
            use_case.cooling_type = cool_types.index(st.session_state.df.loc[i,'cooling_type']) + 1
            use_case.cooling_el_P = st.session_state.cooling_P
            use_case.heating_type = heat_types.index(st.session_state.df.loc[i,'heating_type']) + 1
            use_case.heating_el_P = st.session_state.heating_P
            use_case.background_consumption = st.session_state.df.loc[i, "background_P"]
            use_case.peak_consumption = st.session_state.df.loc[i, "peak_P"]
            use_case.office_start_t = st.session_state.df.loc[i, "office_start"]*60
            use_case.office_end_t = st.session_state.df.loc[i, "office_end"]*60
            use_case.walls_area = st.session_state.df.loc[i, "walls"]
            use_case.U_walls = st.session_state.df.loc[i, "U_walls"]
            use_case.t_set = st.session_state.df.loc[i, "T_set"]
            use_case.floor_area = st.session_state.df.loc[i, "floor_area"]
            use_case.volume_building = st.session_state.df.loc[i, "volume_building"]
            use_case.ach_vent = st.session_state.df.loc[i, "ach_vent"]
            use_case.ventilation_efficiency = st.session_state.df.loc[i, "vent_eff"]
            use_case.thermal_capacitance = st.session_state.df.loc[i, "thermal_cap"]
            use_case.window_area = st.session_state.df.loc[i, "window_area"]
            use_case.U_window = st.session_state.df.loc[i, "U_window"]
            use_case.south_window_area = st.session_state.df.loc[i, "south_window_area"]
            use_case.south_window_azimuth = st.session_state.df.loc[i, "south_window_azimuth"]
            use_case.windows_tilt = st.session_state.df.loc[i, "windows_tilt"]
            use_case.hasEV = random.random() <= penetration_EV/100.0
            use_case.commute_distance_EV = commute_distance_EV
            results_sim = use_case.calculation_BH()
            if i == 1:
                st.session_state.df_results = results_sim
            else:
                st.session_state.df_results = st.session_state.df_results + results_sim
            st.session_state.HVAC_kWh = st.session_state.HVAC_kWh + use_case.HVAC_kWh
            st.session_state.AC_kWh = st.session_state.AC_kWh + use_case.AC_kWh
            st.session_state.energies_heating = st.session_state.energies_heating + use_case.energies_heating
            st.session_state.energies_cooling = st.session_state.energies_cooling + use_case.energies_cooling

            # calculate flexibility for EV of house
            EV_kWh_dom = np.sum(np.abs(results_sim["ElectricVehicle"])) / 4000.0
            if EV_kWh_dom > 1:
                EV_start_time = np.rint(use_case.EV_startTimes[0] / 15)
                EV_end_time = np.rint(use_case.EV_endTimes[0] / 15)
                st.session_state.EV_kWh_dom_flex = st.session_state.EV_kWh_dom_flex + (EV_end_time - EV_start_time) / 96 * EV_kWh_dom
            progress_bar.progress(int(i * 100.0 / building))
        st.session_state.df_results["Business_EV"] = use_case.business_EV_profile(number_of_cars,distance_EV).tolist()
        created_profiles_bool = True
        st.session_state.df_results["OutsideTemp"] = st.session_state.df_results["OutsideTemp"] / building
        progress_bar.progress(100)
    else:
        st.sidebar.warning("All Houses/Buildings are not populated!")
    if len(st.session_state.df_PV) >= st.session_state.number_PV:
        PV = st.session_state.number_PV
        if len(st.session_state.df_PV) >= PV:
            for i in range(1, PV + 1):
                use_case.PV_nominal_power = st.session_state.df_PV.loc[i,'Pn']*1000
                use_case.tiltPV = st.session_state.df_PV.loc[i,'Inclination']
                use_case.azimuthPV = st.session_state.df_PV.loc[i,'Azimuth']
                if i == 1:
                    st.session_state.df_results["Photovoltaic"] = use_case.calculation_PV()
                else:
                    st.session_state.df_results["Photovoltaic"] = st.session_state.df_results["Photovoltaic"] + use_case.calculation_PV()
                progress_bar_PV.progress(int(i * 100.0 / PV))
        progress_bar_PV.progress(100)
    else:
        st.sidebar.warning("All PV systems are not defined!")
with tab6:
    if created_profiles_bool:
        dates = np.arange(0, 24, 0.25)
        st.session_state.df_results.index = dates
        st.session_state.df_results.index.names = ['Time']
        profil1 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='SpringGreen').encode(
            x='Time',
            y='Photovoltaic',
        )
        profil2 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='black').encode(
            x='Time',
            y='ConsumptionHouse'
        )
        # using one chart just to define legend and axis!!!!
        settings = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='black').encode(
            x=alt.X('Time', title="Time [h]"),
            y=alt.Y('ConsumptionHouse', title="Power[W]"),  # we set x and y label only in one chart
            # by setting colors we can define legend for all profiles
            color=alt.Color('Colors:N', scale=alt.Scale(range=['SpringGreen', 'black', 'blue', 'brown', 'red', 'gold'],
                domain=['PV', 'Consumption house', 'EV households', 'Commercial building', 'EV commercial fleet',
                        'Heating/Cooling']),
                legend=alt.Legend(orient='bottom',titleAnchor='middle'))
        )
        profil3 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='blue').encode(
            x='Time',
            y='ElectricVehicle'
        )
        profil4 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='brown', strokeDash=[15, 15]).encode(
            x='Time',
            y='BusinessBuildingProfile'
        )
        profil5 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='red', strokeDash=[15, 15]).encode(
            x='Time',
            y='Business_EV'
        )
        profil6 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='gold', strokeDash=[15, 15]).encode(
            x='Time',
            y='HeatingCoolingDemand_el'
        )
        profiles = alt.layer(profil1, profil2, profil3, profil4, profil5, profil6, settings).properties(title='Electric profiles for zone')
        st.altair_chart(profiles.configure_axis().interactive(), use_container_width=True)

        # second graph
        resize = alt.selection_interval(bind='scales')
        profil2_1 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='red').encode(
            x=alt.X('Time', title='Time [h]'),
            y=alt.Y('HeatingDemand', axis=alt.Axis(title='Power [W]', titleColor='red', tickCount=4))
        )
        profil2_2 = alt.Chart(st.session_state.df_results.reset_index()).mark_line(color='green').encode(
            x='Time',
            y=alt.Y('OutsideTemp', axis=alt.Axis(title='Outside temperature [°C]', titleColor='green'))
        ).add_selection(resize)
        profiles2 = alt.layer(profil2_1, profil2_2).resolve_scale(y='independent').properties(title='Heating demand for zone')
        st.altair_chart(profiles2.configure_axis().interactive(), use_container_width=True)
    else:
        st.info("Run simulation to get results")

with tab7:
    if created_profiles_bool:
        st.write("**Energy needs of the house for a typical day in**", month)
        if com_build_on == 'private house':
            el_kWh = np.sum(st.session_state.df_results["ConsumptionHouse"]) / 4000.0
        else:
            el_kWh = np.sum(st.session_state.df_results["BusinessBuildingProfile"]) / 4000.0
        EV_kWh = 0
        PV_total = np.sum(np.abs(use_case.PVpower)) / 4000.0
        EV_kWh_dom = np.sum(np.abs(st.session_state.df_results["ElectricVehicle"])) / 4000.0
        # No_cars * distance/100km * 16 kWh, 16 kWh per 100km
        EV_kWh_bus = number_of_cars * (distance_EV / 100) * 16
        EV_kWh = EV_kWh_dom + EV_kWh_bus
        # *********************
        #     plot 1         *
        # *********************
        labels = ['HVAC', 'Building\nappliances\nconsumption', 'EV']

        sizes = np.array([(st.session_state.HVAC_kWh + st.session_state.AC_kWh) / 1000.0, el_kWh, EV_kWh])
        total_en = np.sum(sizes)

        fig1, ax1 = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2, 1]})
        # you have to transform from % to values autopct converts array into %!!!!
        ax1[0].pie(sizes, labels=labels,
                   autopct=lambda sizes: '{:.2f}%({:.2f} kWh)'.format(sizes, (sizes / 100.0) * total_en),
                   startangle=140, explode=[0.2, 0.1, 0.1])
        ax1[0].axis('equal')
        labels = ["total energy, electric energy, other energy, PV"]
        ax1[1].bar("total", (st.session_state.HVAC_kWh + st.session_state.AC_kWh) / 1000)
        ax1[1].bar("total", el_kWh, bottom=(st.session_state.HVAC_kWh + st.session_state.AC_kWh) / 1000)
        ax1[1].bar("total", EV_kWh, bottom=(st.session_state.HVAC_kWh + st.session_state.AC_kWh) / 1000 + el_kWh)
        ax1[1].bar("PV", PV_total)
        ax1[1].set_ylabel('Energy [kWh]')
        ax1[1].yaxis.tick_right()
        ax1[1].yaxis.set_label_position("right")
        # ax1.set_title("test")
        fig1.suptitle("Total energy needs")
        st.pyplot(fig1)
        # *********************
        # end plot 1         *
        # *********************
        st.write("----------------------------------------------------------------------------------")
        # *********************
        #     plot 2         *
        # *********************
        fig2, ax2 = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2, 1]})
        labels = ["total energy, electric energy, other energy, PV"]

        ax2[1].bar("total", (st.session_state.energies_heating + st.session_state.energies_cooling) / 1000)
        ax2[1].bar("total", el_kWh, bottom=(st.session_state.energies_heating + st.session_state.energies_cooling) / 1000)
        ax2[1].bar("total", EV_kWh, bottom=(st.session_state.energies_heating + st.session_state.energies_cooling) / 1000 + el_kWh)
        # in case of HVAC or AC show optimized values
        ax2[1].bar("PV", PV_total)
        ax2[1].set_ylabel('Electric energy [kWh]')
        ax2[1].yaxis.tick_right()
        ax2[1].yaxis.set_label_position("right")

        sizes = np.array([(st.session_state.energies_heating + st.session_state.energies_cooling) / 1000.0, el_kWh, EV_kWh])
        total_en = np.sum(sizes)
        labels = ['HVAC', 'Building\nappliances\nconsumption', 'EV']
        # you have to transform from % to values autopct converts array into %!!!!
        ax2[0].pie(sizes, labels=labels,
                   autopct=lambda sizes: '{:.2f}%({:.2f} kWh)'.format(sizes, (sizes / 100.0) * total_en),
                   startangle=140, explode=[0.2, 0.1, 0.1])
        ax2[0].axis('equal')

        fig2.suptitle("Total electric energy needs")
        st.pyplot(fig2)

        # *********************
        # end plot 2         *
        # *********************
        st.write("----------------------------------------------------------------------------------")
        # *********************
        #  flexibility        *
        # *********************
        flexibility_EV = st.session_state.EV_kWh_dom_flex + EV_kWh_bus

        flexibility_HVAC = (st.session_state.energies_heating + st.session_state.energies_cooling) / 1000 / len(use_case.list_of_times_HVAC)
        flexibility_battery = 0
        if use_case.bat_capacity>0:
            flexibility_battery = use_case.bat_capacity * use_case.bat_efficiency
        fig3, ax3 = plt.subplots(1, 2, sharey=True)
        tets = ax3[0].bar("Total energy", (st.session_state.energies_heating + st.session_state.energies_cooling) / 1000, label='HVAC')
        ax3[0].bar("Total energy", el_kWh, bottom=(st.session_state.energies_heating + st.session_state.energies_cooling) / 1000,
                   label='Building appliances\nconsumption')
        ax3[0].bar("Total energy", EV_kWh, bottom=(st.session_state.energies_heating + st.session_state.energies_cooling) / 1000 + el_kWh, label='EV')
        ax3[0].legend()
        ax3[1].bar("Flexible energy", flexibility_EV, label='EV', color='wheat')
        ax3[1].bar("Flexible energy", flexibility_HVAC, bottom=flexibility_EV, label='HVAC', color='tan')
        ax3[1].bar("Flexible energy", flexibility_battery, bottom=flexibility_EV + flexibility_HVAC, label='Battery',
                   color='sienna')
        ax3[1].legend()
        ax3[0].set_ylabel('Electric energy [kWh]')
        fig3.suptitle("Flexibility")
        st.pyplot(fig3)
        needed_bat = (st.session_state.energies_heating + st.session_state.energies_cooling) / 1000 + el_kWh + EV_kWh - flexibility_EV - flexibility_HVAC - flexibility_battery
        # compenzate for return efficiency
        needed_bat /= use_case.bat_efficiency
        if needed_bat > 0:
            st.info('Increase battery capacity for ' + "{:.1f}".format(needed_bat) +
                    ' [kWh] to obtain 100% flexibility')

    else:
        st.info("Run simulation to get results")

with tab8:
    if created_profiles_bool:
        consumption = st.session_state.df_results['HeatingCoolingDemand_el'] + \
                      st.session_state.df_results['ElectricVehicle'] + \
                      st.session_state.df_results['BusinessBuildingProfile'] + \
                      st.session_state.df_results['ConsumptionHouse'] + \
                      st.session_state.df_results['Business_EV']
        production = st.session_state.df_results['Photovoltaic']
        col1, col2, = st.columns([2,1])
        with col1:
            st.image('zone.png')
        with col2:

            st.write("**Maximal Power at substation**")
            st.write("*Power delivered:*",f'{consumption.max()/1000:.2f}',"kWh")
            st.write("*Power generated:*",f'{production.max()/1000:.2f}',"kWh")

            st.write("**Combined Maximal Power at substation**")
            max_el=(consumption - production).max() / 1000
            min_el=(consumption - production).min() / 1000
            if -min_el > max_el:
                st.write("*Power:*",f'{min_el:.2f}',"kWh")
                st.warning("Power generated is higher compared to maximal consumption, "
                           "might lead to overvoltage issues!")
            else:
                st.write("*Power:*", f'{max_el:.2f}', "kWh")
with tab9:
    if created_profiles_bool:
        st.write(st.session_state.df_results)
