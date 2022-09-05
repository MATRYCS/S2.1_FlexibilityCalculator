# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 07:44:06 2022

@author: DSodin
"""

import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import variables
import matplotlib

vehicle = ""
PV_on = ""
EV_on = ""
com_build_on = ""
house_on = ""
battery_on = ""

st.sidebar.write("General parameters")
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
month = st.sidebar.selectbox("Month of the year", months, key = "month")
variables.m = months.index(month)+1
# st.sidebar.write("month is", m)
variables.latitude = st.sidebar.number_input("Latitude [°]", min_value=-90.0, max_value= 90.0, value=46.05, format=None, help = "Geographical latitude, initial value set for Ljubljana/Slovenia")
variables.longitude = st.sidebar.number_input("Longitude [°]", min_value=-180.0, max_value= 180.0, value=14.51, format=None, help = "Geographical longitude, initial value set for Ljubljana/Slovenia")

data = np.array([[variables.latitude,variables.longitude]])

map_data = pd.DataFrame(data,columns=["lat","lon"])

st.sidebar.write("Select assets included in profile generation")

if st.sidebar.checkbox('House'):
    house_on = True

if st.sidebar.checkbox("Commercial building"):
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
    

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Map", "House", "Commercial building", "Photovoltaic", "Electric vehicle",  "Battery", "Create profiles"])
with tab1:
    st.map(map_data)
    
with tab2:
    if house_on:        
        st.write("**Selected building type is: House**")
        window_area = st.number_input("Window area [m²]", min_value=0, max_value=None, value=20, help = "Area of the Glazed Surface in contact with the outside.")
        floor_area = st.number_input("Floor area [m²]", min_value=0, max_value=None, value=500)
        walls_area = st.number_input("Walls area [m²]", min_value=0, max_value=None, value=180, help = "Area of all envelope surfaces, including windows in contact with the outside.")
        volume_building = st.number_input("Building volume [m³]", min_value=0, max_value=None, value=400)
        U_walls =  st.number_input("U value of facade [W/m²K]", min_value=0.0, max_value=None, value=0.2)
        U_windows =  st.number_input("U value of glazed surfaces of windows [W/m²K]", min_value=0.0, max_value=None, value=1.1)
        ach_vent =  st.number_input("U value of glazed surfaces of windows [W/m²K]", min_value=0.0, max_value=1.0, value=0.35, help = "Fraction of air changed per hour through ventilation, 0.35 means approx. one third of air volume is changed in a hour.")
        ventilation_efficiendy = st.number_input("Ventilation efficiency", min_value=0.0, max_value=1.0, value=0.6, help = "The efficiency of the heat recovery system for ventilation. Set to 0 if there is no heat recovery, 1 means heat recovery is 100% effective, no losses from ventilation.")
        t_set = st.number_input("Room temperature [°]", min_value = 15, max_value = 30, value = 20, help = "Set the desired room temperature.")
        thermal_capacitances = [80000, 110000, 165000, 260000, 370000]                                                
        thermal_capacitance_per_floor_area = st.selectbox("Thermal capacitance [J/m²K]", thermal_capacitances, help = "Thermal capacitance of the room. Very light: 80 000, Light: 110 000,  Medium: 165 000, Heavy: 260 000, Very heavy: 370 000")
    else:
        # st.write("Check the house checkbox in order to access its parameters!")
        st.warning('House asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")
        
with tab3:                          
    if com_build_on:
        st.write("**Selected building type is: commercial building**")
        background_power = st.number_input("Background power [W]", min_value=0, max_value=None, value=1000, help = "Consumption of all appliances in the building that can not be turned on or off [W].")
        peak_power = st.number_input("Peak power [W]", min_value=0, max_value=None, value=5000, help = "Peak consumption when all employees are present in their workplace [W].")
        start_hours = [5,6,7,8,9,10,11]
        end_hours = [13,14,15,16,17,18,19]
        start_workDay = st.selectbox("Starting hour of workday", start_hours, index = 4)
        end_workDay = st.selectbox("Ending hour of workday", end_hours, index = 4)
        office_hours=[start_workDay * 60, end_workDay * 60]
    else:
        # st.write("Check the commercial building checkbox in order to access its parameters!")
        st.warning('Commercial building asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")
        
with tab4:
    if PV_on:
        st.header("Parameters")
        variables.PV_nominal_power = st.number_input("Installed peak power of the PV [kWp]", min_value=0, max_value=None, value=10, format=None)
        variables.tiltPV = st.number_input("Inclination/slope [°]", min_value=0, max_value= 90, value=30, format=None, help = "Angle of the PV modules from the horizontal plane")
        variables.azimuthPV = st.number_input("Azimuth [°]", min_value=-180.0, max_value= 180.0, value=0.0, step = 0.1, format=None, help = "The azimuth, or orientation, is the angle of the PV modules relative to the direction due South. - 90° is East, 0° is South and 90° is West.")
    else:
        # st.write("Check the photovoltaic checkbox in order to access its parameters!")
        st.warning('Photovoltaic asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")
        
with tab5: 
    if EV_on:         
        if vehicle == "Hybrid":
            st.write("**Selected type of vehicle is:**", vehicle)
            st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=12.0)
            st.number_input("Charging power [kW]", min_value=0.0, max_value=None, value=3.7)
        if vehicle == "Electric":
            st.write("**Selected type of vehicle is:**", vehicle)
            st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=42.0)
            st.number_input("Charging power [kW]", min_value=0.0, max_value=None, value=7.4)
    else:
        # st.write("Check the electric vehicle checkbox in order to access its parameters!")   
        st.warning('Electric vehicle asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")

with tab6:
    if battery_on:
        st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=15.0, step = 0.1,)
        st.number_input("Peak (dis)charging power [kW]", min_value=0.0, max_value=None, value=5.0, step = 0.1,)
        
    else:
        # st.write("Check the battery checkbox in order to access its parameters!")
        st.warning('Battery asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")

with tab7: 
    run_button = st.button('Create load profiles')
    if run_button:
        import profilegenerator2 
        
        # st.write(profilegenerator2.PVdata)
        # st.write(profilegenerator2.PVpower.values.tolist())
        st.line_chart(pd.DataFrame(profilegenerator2.PVpower, columns = ["PV"]))
        # st.pyplot(charging_profile, label='Electric vehicle', color='m')  # Power [W]
        # st.pyplot(bus_profile, label='business building', color='y')  # Power [W]
        # st.pyplot(HeatingDemand, label='heating demand', color='r')  # Power [Wh/h]
        # st.pyplot(profilegenerator2.PVpower, label='PV', color='g')  # Power [W]
        # st.pyplot(consumption_total_resampled, label='Consumption', color='k')  # Power [W]
        # plt.grid()
        # plt.legend()
        # plt.ylabel('power consumption [W]')
        # plt.xlabel('time 15min slices')
        # plt.show()
        # import matplotlib

