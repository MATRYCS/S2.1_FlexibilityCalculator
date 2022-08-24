# -*- coding: utf-8 -*-
"""
Created on Mon May 30 12:08:15 2022

@author: DSodin
"""


import pandas as pd
import matplotlib.pyplot as plt
import random

startDay = 1 #starting day of simulation
offset = startDay * 24 * 60 #how far off you start
interval = 15 #define the interval of resampled values in minutes 

washMachine = "on"
dishWash = "on"
    
# startDay = houses_matrycs.startDay
washMachineProfile = [66.229735, 119.35574, 162.44595, 154.744551, 177.089979, 150.90621, 170.08704, 134.23536, 331.837935, 2013.922272, 2032.267584, 2004.263808, 2023.32672, 2041.49376, 2012.8128, 2040.140352, 1998.124032, 2023.459776, 1995.309312, 2028.096576, 1996.161024, 552.525687, 147.718924, 137.541888, 155.996288, 130.246299, 168.173568, 106.77933, 94.445568, 130.56572, 121.9515, 161.905679, 176.990625, 146.33332, 173.06086, 145.07046, 188.764668, 88.4058, 117.010432, 173.787341, 135.315969, 164.55528, 150.382568, 151.517898, 154.275128, 142.072704, 171.58086, 99.13293, 94.5507, 106.020684, 194.79336, 239.327564, 152.75808, 218.58576, 207.109793, 169.5456, 215.87571, 186.858018, 199.81808, 108.676568, 99.930348, 151.759998, 286.652289, 292.921008, 300.5829, 296.20425, 195.74251, 100.34136, 312.36975, 287.90921, 85.442292, 44.8647]
dishWasherProfile = [2.343792, 0.705584, 0.078676, 0.078744, 0.078948, 0.079152, 0.079016, 0.078812, 0.941108, 10.449, 4.523148, 34.157214, 155.116416, 158.38641, 158.790988, 158.318433, 158.654276, 131.583375, 13.91745, 4.489968, 1693.082112, 3137.819256, 3107.713851, 3120.197256, 3123.464652, 3114.653256, 3121.27497, 3116.305863, 3106.801566, 3117.703743, 3118.851648, 3110.016195, 3104.806122, 1148.154728, 166.342624, 161.205252, 160.049824, 158.772588, 158.208076, 157.926096, 157.01364, 112.30272, 11.65632, 17.569056, 4.947208, 4.724016, 143.12025, 161.129536, 160.671915, 23.764224, 136.853808, 159.11184, 159.464682, 159.04302, 36.68544, 9.767628, 4.902772, 2239.315008, 3116.846106, 3111.034014, 3118.112712, 3111.809778, 3113.442189, 3110.529708, 3104.676432, 3101.093424, 3121.076178, 1221.232208, 159.964185, 2663.07828, 272.524675, 7.76832, 3.258112, 3.299408, 3.295136, 3.256704, 3.258112, 3.262336, 2224.648744, 367.142872, 4.711025]

startDish = []
startWash = []


#extract dishWasher start and end time of operation and generate random start point      
with open(r'output\Dishwasher_Starttimes.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list of all dishwashers
    for dishWasher in file:
        dishWash_num = dishWasher.split(":")[0] #get the number of house the dishwasher belongs to
        dishWash_string = dishWasher.split(":")[1] #get all the starting times of this dishwasher as a string of starting times
        dishWash_list = dishWash_string.split(",") #make a list of strings; each string its own starting time
        dishWashStarts = [int(start) for start in dishWash_list] #convert strings to integers
        globals()['dishWasher{}'.format(dishWash_num) + 'start'] = dishWashStarts
        for t in dishWashStarts:
            startDish.append((t)/60/24)

with open(r'output\Dishwasher_Endtimes.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list 
    for dishWasher in file:
        dishWash_num = dishWasher.split(":")[0] #get the number of house the dishwasher belongs to
        dishWash_string = dishWasher.split(":")[1] #get all the ending times as a string of ending times
        dishWash_list = dishWash_string.split(",") #make a list of strings; each string its own ending time
        dishWashEnds = [int(end)-len(dishWasherProfile) for end in dishWash_list] #subtract len(dishWasherProfile) , because this is the last moment you can start dishwasher
        globals()['dishWasher{}'.format(dishWash_num) + 'end'] = dishWashEnds              
        globals()['dishWasher{}'.format(dishWash_num)] = []
        for i in range(len(globals()['dishWasher{}'.format(dishWash_num) + 'end'])):
            globals()['dishWasher{}'.format(dishWash_num)].append(random.randint(globals()['dishWasher{}'.format(dishWash_num) + 'start'][i],globals()['dishWasher{}'.format(dishWash_num) + 'end'][i])) #make a starting time of each dishwasher cycle as random start time in cylce interval

#extract WashingMachine start and end time of operation and generate random start point      
with open(r'output\WashingMachine_Starttimes.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list of all WashingMachine
    for WashingMachine in file:
        WashingMachine_num = WashingMachine.split(":")[0] #get the number of house the WashingMachine belongs to
        WashingMachine_string = WashingMachine.split(":")[1] #get all the starting times of this WashingMachine as a string of starting times
        WashingMachine_list = WashingMachine_string.split(",") #make a list of strings; each string its own starting time
        WashingMachineStarts = [int(start) for start in WashingMachine_list] #convert strings to integers
        globals()['WashingMachine{}'.format(WashingMachine_num) + 'start'] = WashingMachineStarts
        for t in WashingMachineStarts:
            startWash.append((t)/60/24)

with open(r'output\WashingMachine_Endtimes.txt', "r") as datafile:
    file = (datafile.read().split()) #read file in 1 list 
    for WashingMachine in file:
        WashingMachine_num = WashingMachine.split(":")[0] 
        WashingMachine_string = WashingMachine.split(":")[1] #get all the ending times as a string of ending times
        WashingMachine_list = WashingMachine_string.split(",") #make a list of strings; each string its own ending time
        WashingMachineEnds = [int(end)-len(washMachineProfile) for end in WashingMachine_list] 
        globals()['WashingMachine{}'.format(WashingMachine_num) + 'end'] = WashingMachineEnds
        globals()['WashingMachine{}'.format(WashingMachine_num)] = []
        for i in range(len(globals()['WashingMachine{}'.format(WashingMachine_num) + 'end'])):
            globals()['WashingMachine{}'.format(WashingMachine_num)].append(random.randint(globals()['WashingMachine{}'.format(WashingMachine_num) + 'start'][i],globals()['WashingMachine{}'.format(WashingMachine_num) + 'end'][i])) 
                     

df = pd.read_csv (r'output\Electricity_Profile.csv', sep= ";", header = None)   #read the csv file (put 'r' before the path string to address any special characters in the path, such as '\'). Don't forget to put the file name at the end of the path + ".csv"
df = df.astype(float) #pretvori dataframe v float, drugače dela z integerji

header = []
for i in range(df.shape[1]): #generiraj številko householda/userja in jo dodaj v header
    header.append(str(i))

df.columns = header
df.head()

if dishWash == "on":
    for user in range(df.shape[1]):
        # print("user =", user)
        try: 
            for startT in globals()['dishWasher{}'.format(user)]:
                print("startT = ", startT)
                print('adding dishWasher profile to user', user)
                count = 0
                for currentP in dishWasherProfile:
                    # print(currentP,df[str(user)][startT+count-offset])                    
                    df[str(user)][startT+count-offset] += currentP
                    # print(startT+count-offset, df[str(user)][startT+count-offset])
                    count += 1
        except:
            print('user', user, 'does not have dishWasher')
else:
    print("dish washers are not included")

if washMachine == "on":
    for user in range(df.shape[1]):
        try: 
            for startT in globals()['WashingMachine{}'.format(user)]:
                print("startT = ", startT)
                print('adding WashingMachine profile to user', user)
                count = 0
                for currentP in washMachineProfile:
                    # print(currentP,df[str(user+1)][startT+count-offset])
                    df[str(user)][startT+count-offset] += currentP
                    # print(startT+count-offset, df[str(user+1)][startT+count-offset])
                    count += 1
        except:
            print('user', user, 'does not have WashingMachine')  
else:
    print("washing machines are not included")              
        

data_len = df.shape[0]
num = int(data_len / interval) #number of bins in new file with average power

new = []
dic = {}
aggregated = []

for j in range(df.shape[1]):
    globals()['user{}'.format(j)] = []    #make empty list for each user
    for i in range(num):
        globals()['user{}'.format(j)].append(sum(df[str(j)][i*interval:(i+1)*interval])/interval) #add average power of the specified interval
    dic["user"+str(j)] = globals()['user{}'.format(j)]  #make dictionary of all users

for i in range(num):
    total = 0
    for j in range(df.shape[1]):
        total += globals()['user{}'.format(j)][i]
    aggregated.append(total)
        
dic["agregated"] = aggregated

df_new = pd.DataFrame(dic)  #create pandas data frame from dictionary

if washMachine == "on" and dishWash == "on":
    file_name = 'Electricity_Profile_'+str(interval)+'min_DishAndWash.csv'
elif washMachine == "on":
    file_name = 'Electricity_Profile_'+str(interval)+'min_Wash.csv'
elif dishWash == "on":
    file_name = 'Electricity_Profile_'+str(interval)+'min_Dish.csv'   
else:
    file_name = 'Electricity_Profile_'+str(interval)+'min.csv'

df_new.to_csv(file_name, index=False)    

    
plt.plot(range(num),aggregated)


# df_dishwash = pd.read_csv (r'C:\Users\DSodin\Desktop\dsodin\software\artificialLoadProfile\output\Dishwasher_Starttimes.txt', sep= ",", header = None)   #read the csv file (put 'r' before the path string to address any special characters in the path, such as '\'). Don't forget to put the file name at the end of the path + ".csv"
