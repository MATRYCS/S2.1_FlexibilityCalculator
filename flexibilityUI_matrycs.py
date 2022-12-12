# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 07:44:06 2022

@author: DSodin, AndrejC
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import profilegenerator2
import altair as alt
import requests
from datetime import datetime

if "start" in st.session_state:
    if (datetime.now() - st.session_state["start"]).total_seconds() > 1800:  # logout reset all parameters!!!!
        if "key" in st.session_state:
            del st.session_state["key"]

def password_entered():
    """Checks whether a password entered by the user is correct."""
    #url = 'http://147.213.76.216:4000/user/get/token'
    url = 'https://matrycs.epu.ntua.gr/security_enabler/user/get/token'
    myobj = {
        "username": st.session_state["username"],
        "password": st.session_state["password"]
    }
    x = requests.post(url, json=myobj)
    # st.write(x.text)
    # st.write(x.status_code)
    print(x.status_code)
    if x.status_code == 200:
        st.session_state["key"] = True
        st.session_state["start"] = datetime.now()
        del st.session_state["password"]
        del st.session_state["username"]
    else:
        st.warning("wrong username or password")

if 'key' not in st.session_state:
    st.title("Login")
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    st.button("Login",on_click=password_entered)


else:
    PV_on = False
    EV_on = False
    com_build_on = False
    number_of_cars=1
    distance_EV = 0
    battery_on = False
    created_profiles_bool=False

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

    b_types = ['private house','commercial building']
    com_build_on = st.sidebar.radio('Type of building', b_types)
    priv_com = b_types.index(com_build_on)

    if st.sidebar.checkbox('Photovoltaics'):
        PV_on = True

    if st.sidebar.checkbox('Electric Vehicle'):
        EV_on = True

    if st.sidebar.checkbox('Battery'):
        battery_on = True



    st.title("Matrycs - Catalogue service")


    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🗺️Map", "📃Building thermal profile", "📃User profile", "📃PV", "📃EV",  "📃Battery", "📈Profiles",  "	📊Flexibility"])
    with tab1:
        st.map(map_data)

    with tab2:
        st.write("**Heating / cooling parameters**")
        heat_types = ["Heat pump", "Electric heater", "Other"]
        cool_types = ["Air conditioner", "Other"]

        col1, col2, = st.columns(2)
        with col1:
            heating_type = st.selectbox("Type of heating", heat_types)

        with col2:
            cooling_type = st.selectbox("Type of cooling", cool_types)

        use_case.heating_type = heat_types.index(heating_type)+1
        use_case.cooling_type = cool_types.index(cooling_type)+1

        col1, col2, = st.columns(2)
        with col1:
            heating_el_P = st.number_input("Max electrical power of heating device [W]",
                                min_value=0, max_value=None, value=3000,
                                help = "This is the el. power of the device in the case of HVAC, the COP "
                                       "(Coefficient Of Performance) number will increase the heating power of HVAC")

        with col2:
            cooling_el_P = st.number_input("Max electrical power of cooling device [W]",
                                min_value=0, max_value=None, value=2000,
                                help = "This is the el. power of the device in case of air conditioning, the COP "
                                       "(Coefficient Of Performance) number will increase the cooling power")
        st.write("----------------------------------------------------------------------------------")


        st.write("**Rooms parameters**")
        room_param = st.radio("Type of known rooms parameters", ["Basic", "Advanced"], help ="When basic option is selected some of the parameters will be automatically generated as typicall values. Choose advanced option if all parameters are known.")
        col5, col6 = st.columns(2)
        with col5:
            use_case.walls_area = st.number_input("Walls area [m²]", min_value=0, max_value=None, value=400, help = "Area of all envelope surfaces, including windows in contact with the outside.")

        with col6:
            use_case.U_walls =  st.number_input("U value of facade [W/m²K]", min_value=0.0, max_value=None, value=0.2)

        use_case.t_set = st.number_input("Room temperature [°]", min_value = 15, max_value = 30, value = 20, help = "Set the desired room temperature.")

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
            use_case.ventilation_efficiendy = 0.6
            st.write("The efficiency of the heat recovery system for ventilation: 0 if there is no heat recovery, 1 if heat recovery is 100% effective. Currently selected value is:", use_case.ach_vent)
            use_case.thermal_capacitance = 165000
            st.write("Thermal capacitance of the room [J/m²K]. Currently selected value is:", use_case.thermal_capacitance)

        if room_param == "Advanced":
            use_case.floor_area = st.number_input("Floor area [m²]", min_value=0, max_value=None, value=500)
            use_case.volume_building = st.number_input("Building volume [m³]", min_value=0, max_value=None, value=400)
            use_case.ach_vent =  st.number_input("Fraction of air mass exchanged through ventilation", min_value=0.0, max_value=1.0, value=0.35, help = "Fraction of air changed per hour through ventilation, 0.35 means approx. one third of air volume is changed in a hour.")
            use_case.ventilation_efficiendy = st.number_input("Ventilation efficiency", min_value=0.0, max_value=1.0, value=0.6, help = "The efficiency of the heat recovery system for ventilation. Set to 0 if there is no heat recovery, 1 means heat recovery is 100% effective, no losses from ventilation.")
            thermal_capacitances = [80000, 110000, 165000, 260000, 370000]
            use_case.thermal_capacitance = st.selectbox("Thermal capacitance [J/m²K]", thermal_capacitances, help = "Thermal capacitance of the room. Very light: 80 000, Light: 110 000,  Medium: 165 000, Heavy: 260 000, Very heavy: 370 000", index = 2)

        st.write("----------------------------------------------------------------------------------")
        st.write("**Windows parameters**")
        win_param = st.radio("Type of known windows parameters", ["Basic", "Advanced"], help ="When basic option is selected some of the parameters will be automatically generated as typicall values. Choose advanced option if all parameters are known.")
        col3, col4 = st.columns(2)
        with col3:
            use_case.window_area = st.number_input("Window area [m²]", min_value=0, max_value=None, value=20, help = "Area of the Glazed Surface in contact with the outside.")

        with col4:
            use_case.U_windows = st.number_input("U value of glazed surfaces of windows [W/m²K]", min_value=0.0, max_value=None, value=1.1)

        if win_param == "Basic":
            st.write("Assumed value of south window area is 1/3 of entire window area. Current south window area =", round(use_case.window_area/3, 2),  "[m²].")
            use_case.south_window_area /= 3
            use_case.south_window_azimuth = 0
            st.write("Azimuth of windows is the angle of the windows relative to the direction due South [- 90° is East, 0° is South and 90° is West.]. Currently assumed orientation of windows is:", use_case.south_window_azimuth,"°.")
            use_case.windows_tilt = 90
            st.write("Inclination slope is the angle of the windows from the horizontal plane. Currently assumed value is:", use_case.windows_tilt, "°.")

        if win_param == "Advanced":
            use_case.south_window_area = st.number_input("South window area [m²]", min_value=0, max_value=None, value=10, help = "Area of windows facing the south.")
            use_case.south_window_azimuth = st.number_input("Azimuth of south windows [°]", min_value=-90, max_value=90, value=0, help = "The azimuth, or orientation, is the angle of the windows relative to the direction due South. - 90° is East, 0° is South and 90° is West.")
            use_case.windows_tilt = st.number_input("Inclination/slope [°]", min_value=0, max_value=90, value=90, help = "Angle of the south windows from the horizontal plane")

    with tab3:
        if priv_com==0:
            types_of_family = ["Single worker", "Single jobless", "Single part-time", "Couple", "Dual worker", "Family dual parent", "Family dual worker", "Family single parent", "Dual retired", "Single retired"]
            type_of_family = st.selectbox("Type of household", types_of_family)

        else:
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
        if priv_com==0:
            use_case.EV_capacity = st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=12.0)*1000
            use_case.EV_power = st.number_input("Charging power [kW]", min_value=0.0, max_value=None, value=3.7)*1000

        else:
            number_of_cars = st.number_input("Number of vehicles:", min_value=0, max_value=None, value=1,
                                                   help="Total number of all EV vehicles in the fleet.")
            distance_EV = st.number_input("Average daily distance done by vehicle [km]", min_value=0, max_value=None, value=20,
                                                   help="Average daily distance of EV vehicles, you can estimate the total distance divided by the number of vehicles")

    with tab6:
        if battery_on:
            use_case.bat_capacity = st.number_input("Battery capacity [kWh]", min_value=0.0, max_value=None, value=15.0, step = 0.1,)
            use_case.bat_power = st.number_input("Peak (dis)charging power [kW]", min_value=0.0, max_value=None, value=5.0, step = 0.1,)
            use_case.bat_efficiency = st.number_input("Charging efficiency [%]", min_value=0.0, max_value=100.0, value=90.0, help = "Efficiency of battery charging/discharging.")/100
        else:
            # st.write("Check the battery checkbox in order to access its parameters!")
            st.warning('Battery asset is not selected under general parameters! Please check its checkbox in order to access parameters.', icon="⚠️")

    run_button = st.sidebar.button('Calculate profiles')
    if run_button:
        use_case.calculation()
        created_profiles_bool = True

    with tab7:
        if created_profiles_bool:
            dates=np.arange(0, 24, 0.25)
            use_case.dailyResults.index=dates
            use_case.dailyResults.index.names=['Time']
            profil1=alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='SpringGreen').encode(
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
                color=alt.Color('Color:N', scale=alt.Scale(range=['SpringGreen', 'black', 'blue', 'brown'],
                                                    domain=['PV', 'Consumption house', 'EV', 'Commercial building']))
            )
            profil3=alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='blue').encode(
                x='Time',
                y='ElectricVehicle'
            )
            profil4=alt.Chart(use_case.dailyResults.reset_index()).mark_line(color='brown',strokeDash=[15, 15]).encode(
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
        else:
            st.info("Run simulation to get results")

    with tab8:
        if created_profiles_bool:
            st.write("**Energy needs of the house for a typical day in**", month)
            if priv_com == 0:
                el_kWh = np.sum(use_case.consumption_total_resampled)/4000.0
            else:
                el_kWh = np.sum(use_case.bus_profile)/4000.0
            HVAC_kWh=0
            AC_kWh=0
            EV_kWh=0
            PV_total=np.sum(np.abs(use_case.PVpower)) / 4000.0
            if PV_on is False:
                PV_total = 0
            for en in use_case.list_of_energies_HVAC:
                if en>0:
                    HVAC_kWh +=en
                else:
                    AC_kWh -=en


            if EV_on:
                if priv_com == 0:
                    EV_kWh = np.sum(np.abs(use_case.charging_profile))/4000.0
                else:
                    # No_cars * distance/100km * 16 kWh, 16 kWh per 100km
                    EV_kWh = number_of_cars*(distance_EV/100)*16
            #*********************
            #     plot 1         *
            #*********************
            labels=['HVAC','Building\nappliances\nconsumption','EV']

            sizes=np.array([(HVAC_kWh+AC_kWh)/1000.0,el_kWh,EV_kWh])
            total_en=np.sum(sizes)

            fig1, ax1 = plt.subplots(1,2,gridspec_kw={'width_ratios': [2, 1]})
            # you have to transform from % to values autopct converts array into %!!!!
            ax1[0].pie(sizes, labels=labels, autopct=lambda sizes: '{:.2f}%({:.2f} kWh)'.format(sizes,(sizes/ 100.0) * total_en),
                     startangle=140,explode=[0.2,0.1,0.1])
            ax1[0].axis('equal')
            labels=["total energy, electric energy, other energy, PV"]
            ax1[1].bar("total",(HVAC_kWh+AC_kWh)/1000)
            ax1[1].bar("total",el_kWh, bottom=(HVAC_kWh+AC_kWh)/1000)
            ax1[1].bar("total", EV_kWh, bottom=(HVAC_kWh + AC_kWh) / 1000+el_kWh)
            ax1[1].bar("PV", PV_total)
            ax1[1].set_ylabel('Energy [kWh]')
            ax1[1].yaxis.tick_right()
            ax1[1].yaxis.set_label_position("right")
            #ax1.set_title("test")
            fig1.suptitle("Total energy needs")
            st.pyplot(fig1)
            #*********************
            # end plot 1         *
            #*********************
            st.write("----------------------------------------------------------------------------------")
            #*********************
            #     plot 2         *
            #*********************
            fig2, ax2 = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2, 1]})
            labels=["total energy, electric energy, other energy, PV"]
            if use_case.heating_type==1:
                HVAC_energies = []
                for x in range(96):
                    HVAC_energies.append(use_case.HVAC_COP(use_case.OutsideTemp[x]) * heating_el_P / 4.0)

                # calculating HVAC energies
                energies_heating = 0
                energies_heating_optimized = 0
                for i in range(len(use_case.list_of_times_HVAC)):
                    t_start = use_case.list_of_times_HVAC[i - 1]
                    t_end = use_case.list_of_times_HVAC[i]
                    if len(use_case.list_of_times_HVAC) == 1:
                        t_end = 96
                        t_start = 1
                    delta = t_end - t_start
                    if delta < 0:
                        delta += 96
                    # ordered energies for each timestamp, first calculate default value for time and after that optimal
                    energies_timestamp = np.roll(HVAC_energies, -t_start)[:delta]
                    # not optimized
                    list_en = use_case.list_of_energies_HVAC[i]
                    if list_en < 0:
                        continue
                    for en in energies_timestamp:
                        if en <= 0:
                            break
                        elif en < (list_en / 4.0):
                            list_en -= en / 4.0
                            energies_heating += heating_el_P / 4.0
                        else:  # only some leftovers
                            energies_heating += (list_en / en) * heating_el_P / 4.0
                            break

                    # optimized scenario, since these are monotonic functions we can just reorder the list and operate
                    # with first values
                    energies_timestamp[::-1].sort()
                    list_en = use_case.list_of_energies_HVAC[i]
                    for en in energies_timestamp:
                        if en <= 0:
                            break
                        elif en < (list_en / 4.0):
                            list_en -= en / 4.0
                            energies_heating_optimized += heating_el_P / 4.0
                        else:  # only some leftovers
                            energies_heating_optimized += (list_en / en) * heating_el_P / 4.0
                            break
            elif use_case.heating_type==2:
                energies_heating=HVAC_kWh
            else:
                energies_heating=0

            if use_case.cooling_type == 1:
                AC_energies = []
                for x in range(96):
                    AC_energies.append(
                        -use_case.airconditioner_COP(use_case.t_set, use_case.OutsideTemp[x]) * cooling_el_P / 4.0)
                # calculating AC energies
                energies_cooling = 0
                energies_cooling_optimized = 0
                for i in range(len(use_case.list_of_times_HVAC)):
                    t_start = use_case.list_of_times_HVAC[i - 1]
                    t_end = use_case.list_of_times_HVAC[i]
                    if len(use_case.list_of_times_HVAC) == 1:
                        t_end = 96
                        t_start = 1
                    delta = t_end - t_start
                    if delta < 0:
                        delta += 96
                    # ordered energies for each timestamp, first calculate default value for time and after that optimal
                    energies_timestamp = np.roll(AC_energies, -t_start)[:delta]
                    # not optimized
                    list_en = use_case.list_of_energies_HVAC[i]
                    if list_en > 0:
                        continue
                    for en in energies_timestamp:
                        if en >= 0:
                            break
                        elif en > (list_en / 4.0):
                            list_en -= en / 4.0
                            energies_cooling += cooling_el_P / 4.0
                        else:  # only some leftovers
                            energies_cooling += (list_en / en) * cooling_el_P / 4.0
                            break

                    # optimized scenario, since these are monotonic functions we can just reorder the list and operate
                    # with first values
                    energies_timestamp.sort()
                    list_en = use_case.list_of_energies_HVAC[i]
                    for en in energies_timestamp:
                        if en >= 0:
                            break
                        elif en > (list_en / 4.0):
                            list_en -= en / 4.0
                            energies_cooling_optimized += cooling_el_P / 4.0
                        else:  # only some leftovers
                            energies_cooling_optimized += (list_en / en) * cooling_el_P / 4.0
                            break
            else:
                energies_cooling=0

            ax2[1].bar("total",(energies_heating+energies_cooling)/1000)
            ax2[1].bar("total",el_kWh, bottom=(energies_heating+energies_cooling)/1000)
            ax2[1].bar("total", EV_kWh, bottom=(energies_heating + energies_cooling) / 1000+el_kWh)
            # in case of HVAC or AC show optimized values
            ax2[1].bar("PV", PV_total)
            ax2[1].set_ylabel('Electric energy [kWh]')
            ax2[1].yaxis.tick_right()
            ax2[1].yaxis.set_label_position("right")

            sizes = np.array([(energies_heating + energies_cooling) / 1000.0, el_kWh, EV_kWh])
            total_en = np.sum(sizes)
            labels = ['HVAC', 'Building\nappliances\nconsumption', 'EV']
            # you have to transform from % to values autopct converts array into %!!!!
            ax2[0].pie(sizes, labels=labels,
                       autopct=lambda sizes: '{:.2f}%({:.2f} kWh)'.format(sizes, (sizes / 100.0) * total_en),
                       startangle=140, explode=[0.2, 0.1, 0.1])
            ax2[0].axis('equal')

            fig2.suptitle("Total electric energy needs")
            st.pyplot(fig2)
            if ((use_case.heating_type==1) and (energies_heating>0)):
                st.write("Heat pump energies optimized additional savings:", int(energies_heating-energies_heating_optimized), 'Wh')
            if ((use_case.cooling_type==1) and (energies_cooling>0)):
                st.write("Air conditioner energies optimized additional savings:", int(energies_cooling-energies_cooling_optimized), 'Wh')

            #*********************
            # end plot 2         *
            #*********************
            st.write("----------------------------------------------------------------------------------")
            # *********************
            #  flexibility        *
            # *********************
            EV_start_time= np.rint(use_case.EV_startTimes[0]/15)
            EV_end_time = np.rint(use_case.EV_endTimes[0]/15)
            flexibility_EV=0
            if EV_on:
                if priv_com == 0:
                    flexibility_EV=(EV_end_time-EV_start_time)/96*EV_kWh
                    if EV_start_time>95:
                        EV_start_time-=96
                    if EV_end_time>95:
                        EV_end_time-=96
                else:
                    flexibility_EV = EV_kWh

            flexibility_HVAC = (energies_heating+energies_cooling)/1000/len(use_case.list_of_times_HVAC)
            flexibility_battery = 0
            if battery_on:
                flexibility_battery = use_case.bat_capacity*use_case.bat_efficiency
            fig3, ax3 = plt.subplots(1,2,sharey=True)
            tets=ax3[0].bar("Total energy",(energies_heating+energies_cooling)/1000,label='HVAC')
            ax3[0].bar("Total energy",el_kWh, bottom=(energies_heating+energies_cooling)/1000,label='Building appliances\nconsumption')
            ax3[0].bar("Total energy", EV_kWh, bottom=(energies_heating + energies_cooling) / 1000+el_kWh,label='EV')
            ax3[0].legend()
            ax3[1].bar("Flexible energy", flexibility_EV, label='EV', color='wheat')
            ax3[1].bar("Flexible energy", flexibility_HVAC,bottom=flexibility_EV, label='HVAC',color='tan')
            ax3[1].bar("Flexible energy", flexibility_battery, bottom=flexibility_EV+flexibility_HVAC, label='Battery',color='sienna')
            ax3[1].legend()
            ax3[0].set_ylabel('Electric energy [kWh]')
            fig3.suptitle("Flexibility")
            st.pyplot(fig3)
            needed_bat = (energies_heating + energies_cooling) / 1000 + el_kWh + EV_kWh - flexibility_EV - flexibility_HVAC - flexibility_battery
            # compenzate for return efficiency
            needed_bat /= use_case.bat_efficiency
            if needed_bat>0:
                st.info('Increase battery capacity for '+"{:.1f}".format(needed_bat)+
                    ' [kWh] to obtain 100% flexibility')

        else:
            st.info("Run simulation to get results")

