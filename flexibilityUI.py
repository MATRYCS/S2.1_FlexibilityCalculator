# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 07:44:06 2022

@author: DSodin, AndrejC
"""

import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import matplotlib
import profilegenerator2
import altair as alt

vehicle = ""
PV_on = ""
EV_on = ""
com_build_on = ""
house_on = ""
battery_on = ""
house_family = ""

use_case = profilegenerator2.profilgenerator2()

st.sidebar.write("General parameters")
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
month = st.sidebar.selectbox("Month of the year", months, key = "month")
use_case.month = months.index(month)+1
# st.sidebar.write("month is", m)
use_case.latitude = st.sidebar.number_input("Latitude [°]", min_value=-90.0, max_value= 90.0, value=46.05, format=None, help = "Geographical latitude, initial value set for Ljubljana/Slovenia")
use_case.longitude = st.sidebar.number_input("Longitude [°]", min_value=-180.0, max_value= 180.0, value=14.51, format=None, help = "Geographical longitude, initial value set for Ljubljana/Slovenia")

data = np.array([[use_case.latitude,use_case.longitude]])

map_data = pd.DataFrame(data,columns=["lat","lon"])

st.sidebar.write("Select assets included in profile generation")

if st.sidebar.checkbox('Thermal building profile'):
    house_on = True

if st.sidebar.checkbox("User profile"):
    com_build_on = True    
    
if st.sidebar.checkbox('Photovoltaics'):
    PV_on = True
 
if st.sidebar.checkbox('Electric Vehicle'):
    EV_on = True
    EV_names = ["Hybrid", "Electric"]
    vehicle = st.sidebar.radio('Type of vehicle', EV_names)
    
if st.sidebar.checkbox('Battery'):
    battery_on = True
    

st.title("Matrycs - Profile generator")    
    

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Map", "Thermal building profile", "User profile", "Photovoltaic", "Electric vehicle",  "Battery", "Create profiles",  "Flexibility"])
with tab1:
    st.map(map_data)
    
with tab2:
    if house_on:      
        st.write("**Thermal building profile**")
        heat_types = ["HVAC", "Electric heater", "Other"]
        heating_type = st.selectbox("Type of heating", heat_types)
        cool_types = ["Air conditioner", "Other"]
        cooling_type = st.selectbox("Type of cooling", cool_types)
        use_case.heating_type = heat_types.index(heating_type)+1
        use_case.cooling_type = cool_types.index(cooling_type)+1        
        use_case.window_area = st.number_input("Window area [m²]", min_value=0, max_value=None, value=20, help = "Area of the Glazed Surface in contact with the outside.")
        use_case.south_window_area = st.number_input("South window area [m²]", min_value=0, max_value=None, value=10, help = "Area of windows facing the south.")
        use_case.south_window_azimuth = st.number_input("Azimuth of south windows [°]", min_value=-90, max_value=90, value=0, help = "The azimuth, or orientation, is the angle of the PV modules relative to the direction due South. - 90° is East, 0° is South and 90° is West.")
        use_case.windows_tilt = st.number_input("Inclination/slope [°]", min_value=0, max_value=90, value=90, help = "Angle of the south windows from the horizontal plane")
        use_case.floor_area = st.number_input("Floor area [m²]", min_value=0, max_value=None, value=500)
        use_case.walls_area = st.number_input("Walls area [m²]", min_value=0, max_value=None, value=180, help = "Area of all envelope surfaces, including windows in contact with the outside.")
        use_case.volume_building = st.number_input("Building volume [m³]", min_value=0, max_value=None, value=400)
        use_case.U_walls =  st.number_input("U value of facade [W/m²K]", min_value=0.0, max_value=None, value=0.2)
        use_case.U_windows =  st.number_input("U value of glazed surfaces of windows [W/m²K]", min_value=0.0, max_value=None, value=1.1)
        use_case.ach_vent =  st.number_input("U value of glazed surfaces of windows [W/m²K]", min_value=0.0, max_value=1.0, value=0.35, help = "Fraction of air changed per hour through ventilation, 0.35 means approx. one third of air volume is changed in a hour.")
        use_case.ventilation_efficiendy = st.number_input("Ventilation efficiency", min_value=0.0, max_value=1.0, value=0.6, help = "The efficiency of the heat recovery system for ventilation. Set to 0 if there is no heat recovery, 1 means heat recovery is 100% effective, no losses from ventilation.")
        use_case.t_set = st.number_input("Room temperature [°]", min_value = 15, max_value = 30, value = 20, help = "Set the desired room temperature.")
        thermal_capacitances = [80000, 110000, 165000, 260000, 370000]                                                
        use_case.thermal_capacitance = st.selectbox("Thermal capacitance [J/m²K]", thermal_capacitances, help = "Thermal capacitance of the room. Very light: 80 000, Light: 110 000,  Medium: 165 000, Heavy: 260 000, Very heavy: 370 000")
         
    else:
        # st.write("Check the house checkbox in order to access its parameters!")
        st.warning('Thermal building asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")
        
with tab3:                          
    if com_build_on:
        tab_1, tab_2 = st.tabs(["Private","Commercial"])
        with tab_1:
            if st.checkbox('Include private houses'):
                house_family = True
            types_of_family = ["Single worker", "Single jobless", "Single part-time", "Couple", "Dual worker", "Family dual parent", "Family dual worker", "Family single parent", "Dual retired", "Single retired"]
            type_of_family = st.selectbox("Type of household", types_of_family)
            
        with tab_2:
            st.write("**Commercial**")
            use_case.background_consumption = st.number_input("Background power [W]", min_value=0, max_value=None, value=1000, help = "Consumption of all appliances in the building that can not be turned off [W].")
            use_case.peak_consumption = st.number_input("Peak power [W]", min_value=0, max_value=None, value=5000, help = "Peak consumption when all employees are present in their workplace [W].")
            start_hours = [5,6,7,8,9,10,11]
            end_hours = [13,14,15,16,17,18,19]
            use_case.office_start_t = st.selectbox("Starting hour of workday", start_hours, index = 4)*60
            use_case.office_end_t = st.selectbox("Ending hour of workday", end_hours, index = 4)*60
            # office_hours=[start_workDay * 60, end_workDay * 60]
            types_of_day = ["Workday","Weekend"]
            type_of_day = st.selectbox("Weekend or workday", types_of_day)
            use_case.weekend = types_of_day.index(type_of_day) 
        
    else:
        # st.write("Check the commercial building checkbox in order to access its parameters!")
        st.warning('Commercial building asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")
        
with tab4:
    if PV_on:
        st.header("Parameters")
        use_case.PV_nominal_power = st.number_input("Installed peak power of the PV [kWp]", min_value=0.0, max_value=None, value=5.0, format=None)*1000
        use_case.tiltPV = st.number_input("Inclination/slope [°]", min_value=0, max_value= 90, value=30, format=None, help = "Angle of the PV modules from the horizontal plane")
        use_case.azimuthPV = st.number_input("Azimuth [°]", min_value=-180.0, max_value= 180.0, value=0.0, step = 0.1, format=None, help = "The azimuth, or orientation, is the angle of the PV modules relative to the direction due South. - 90° is East, 0° is South and 90° is West.")
    else:
        # st.write("Check the photovoltaic checkbox in order to access its parameters!")
        st.warning('Photovoltaic asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")
        
with tab5: 
    if EV_on:         
        if vehicle == "Hybrid":
            st.write("**Selected type of vehicle is:**", vehicle)
            use_case.EV_capacity = st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=12.0)
            use_case.EV_power = st.number_input("Charging power [kW]", min_value=0.0, max_value=None, value=3.7)
        if vehicle == "Electric":
            st.write("**Selected type of vehicle is:**", vehicle)
            st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=42.0)
            st.number_input("Charging power [kW]", min_value=0.0, max_value=None, value=7.4)
    else:
        # st.write("Check the electric vehicle checkbox in order to access its parameters!")   
        st.warning('Electric vehicle asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")

with tab6:
    if battery_on:
        use_case.bat_capacity = st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=15.0, step = 0.1,)
        use_case.bat_power = st.number_input("Peak (dis)charging power [kW]", min_value=0.0, max_value=None, value=5.0, step = 0.1,)
        use_case.bat_efficiency = st.number_input("Charging efficiency [%]", min_value=0.0, max_value=100.0, value=90.0, help = "Efficiency of battery charging/discharging.")/100
    else:
        # st.write("Check the battery checkbox in order to access its parameters!")
        st.warning('Battery asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")

with tab7: 
    run_button = st.button('Create load profiles')
    if run_button:
        use_case.calculation()
        #dates = pd.date_range(pd.Timestamp(2016, 1, 1, 00, 00), pd.Timestamp(2016, 1, 1, 23, 59), freq="15min",
        #                      tz='UTC').strftime("%H:%M")
        dates=np.arange(0, 24, 0.25)
        use_case.dailyResults.index=dates
        use_case.dailyResults.index.names=['Time']
        profil1=alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='green').encode(
            x='Time',
            y='Photovoltaic',
        )
        profil2 = alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='black').encode(
            x='Time',
            y='ConsumptionHouse'
        )
        #using one chart just to define legend and axis!!!!
        settings = alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='black').encode(
            x=alt.X('Time',title="Time [h]"),
            y=alt.Y('ConsumptionHouse',title="Power[W]"), # we set x and y label only in one chart
            # by setting colors we can define legend for all profiles
            color=alt.Color('Color:N', scale=alt.Scale(range=['green', 'black', 'blue', 'dimgray'],
                                                domain=['PV', 'Consumption house', 'EV/PHEV', 'Commercial building']))
        )
        profil3=alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='blue').encode(
            x='Time',
            y='ElectricVehicle'
        )
        profil4=alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='dimgray',strokeDash=[15, 15]).encode(
            x='Time',
            y='BusinessBuildingProfile'
        )
        profiles=alt.layer(profil1,profil2,profil3,profil4,settings).properties(title='Electric profiles')
        st.altair_chart(profiles.configure_axis().interactive(),use_container_width=True)

        #second graph
        resize = alt.selection_interval(bind='scales')
        profil2_1 = alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='red').encode(
            x=alt.X('Time', title='Time [h]'),
            y=alt.Y('HeatingDemand', axis=alt.Axis(title='Power [W]', titleColor='red', tickCount=4))
        )
        profil2_2 = alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='green').encode(
            x='Time',
            y=alt.Y('OutsideTemp',axis=alt.Axis(title='Outside temperature [°C]',titleColor='green'))
        ).add_selection(resize)
        profiles2 = alt.layer(profil2_1, profil2_2).resolve_scale(y='independent').properties(title='Heating demand')
        st.altair_chart(profiles2.configure_axis().interactive(), use_container_width=True)
        st.write(use_case.list_of_times_HVAC)

with tab8:
    #run_button2 = st.button('Calculate flexibility potential')
    #if run_button2:
    st.write(use_case.list_of_times_HVAC)
    st.write(use_case.list_of_energies_HVAC)