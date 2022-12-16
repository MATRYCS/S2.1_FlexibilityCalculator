# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 07:44:06 2022

@authors: Andrej Campa, Denis Sodin
"""

import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import profilegenerator2
import altair as alt

PV_on = False
EV_on = False
com_build_on = False
number_of_cars = 1
distance_EV = 0
battery_on = False
created_profiles_bool = False

def save_values(value):
    # save state parameters!
    if value == 'radio_BH':
        st.session_state.df.loc[st.session_state.building_no,'type_building'] = st.session_state.radio_BH
    print("Saving state:", st.session_state.df)


# define all possible states
# dataframe for storing houses types, building envelope parameters and HVAC details
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['type_building', 'type_of_family', 'cooling_type', 'cooling_el_p',
                                                'heating_type', 'heating_el_P'])
    # initialize all values
    st.session_state.df.loc[1] = ['private house', "Single worker",  "Air conditioner", 3000,  "Heat pump", 2000]
    st.session_state.radio_BH = 'private house'
    st.session_state.family = "Single worker"
    st.session_state.cooling_type = "Air conditioner"
    st.session_state.cooling_P = 2000
    st.session_state.heating_type = "Heat pump"
    st.session_state.heating_P = 3000

col1, col2, = st.columns(2)
with col2:
    st.session_state.number_buildings = st.number_input("Maximum number of buildings in zones",
                                   min_value=1, max_value=None, value=1,
                                   help="Specify the number of buildings in the zone.")
with col1:
    #st.text(st.session_state.number_buildings)
    st.session_state.building_no = st.number_input("Selected building",
                                   min_value=1, max_value=st.session_state.number_buildings,value=1,
                                                   args=("radio_BH",),
                                   help="Used to scroll through individual building perameters.")
# initialize all values
#print("test\n\n", st.session_state.building_no in st.session_state.df.index)
if st.session_state.building_no not in st.session_state.df.index:
    st.session_state.df.loc[st.session_state.building_no] = ['private house', "Single worker", "Air conditioner", 3000, "Heat pump", 2000]
b_types = ['private house', 'commercial building']
print("type",st.session_state.df.loc[st.session_state.building_no,"type_building"])
st.session_state.radio_BH = st.session_state.df.loc[st.session_state.building_no,"type_building"]
com_build_on = st.radio('Select type of the building', b_types, key="radio_BH",on_change=save_values, args =("radio_BH",))
print("type1",com_build_on)
st.write("----------------------------------------------------------------------------------")
types_of_family = ["Single worker", "Single jobless", "Single part-time", "Couple", "Dual worker",
                   "Family dual parent", "Family dual worker", "Family single parent", "Dual retired",
                   "Single retired"]
if com_build_on == 'private house':
    st.write("**Household patrameters**")
    type_of_family = st.selectbox("Type of household", types_of_family, key='family')
    st.write("----------------------------------------------------------------------------------")

else:
    type_of_family = "Single worker"
    st.write("**Commercial**")


st.write("**Heating / cooling parameters**")
heat_types = ["Heat pump", "Electric heater", "Other"]
cool_types = ["Air conditioner", "Other"]

col1, col2, = st.columns(2)
with col1:
    heating_type = st.selectbox("Type of heating", heat_types, key='heating_type' )

with col2:
    cooling_type = st.selectbox("Type of cooling", cool_types, key='cooling_type')
