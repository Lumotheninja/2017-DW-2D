# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 14:43:54 2017

@author: Lumotheninja
"""

import matplotlib.pyplot as plt
import simpy

'''
We are simulating the algae bottle lying down, exposed to change in temperature of the environment and 
the sun which is shining onto it. The temperature is monitored by a controller, which outputs pwm signals
to a water pump running on 5W which acts a heat exchanger to cool it down

Instead of serial communication between the simulator and the controller, this code provides a proportional
derivative controller which is coded as a process in simpy
'''

#constants used
hourly_temperature = [26.5,26.5,26.5,26.5,26.5,26.5,26.5,27.5,28.5,29.5,30.5,30.5,30.5,30.5,30.5,30.5,29.5,29.5,28.5,28.5,27.5,27.5,27.5,27.5]
hourly_sun_duration=[0,0,0,0,0,0,0,0.1,0.35,0.75,0.75,0.75,0.65,0.65,0.55,0.45,0.3,0.05,0,0,0,0,0,0] #data obtained from meteorological services Singapore
threshold=30 #temperature we want to maintain
heat_transfer_coefficient=50 #the bottle's heat transfer coefficient, experimentally determined
area_of_bottle=0.00325 #the area of bottle of one side
simtime=604800 #the time of simulation which is one week
mass= 105 #mass of the bottle with water
heat_capacity= 4.2 #heat capacity of water, we asuumed perfect conduction through the plexiglass
cop = 2.5 #coefficient of performance of motor as a heat pump,experimentally determined


#Process1 - adds heat into algae bottle by convection
def temp_flux(env,ambient_temperature): 
       #function to model hourly temperature flux according to data
       while True:
              count =0
              while count <= 23:
                     if count ==23:
                            temp_diff = (hourly_temperature[0]-hourly_temperature[count])/3600
                     else:
                            temp_diff = (hourly_temperature[count+1]-hourly_temperature[count])/3600
                            hour_second_count=0
                            while hour_second_count<3600:
                                   temp_change=(hourly_temperature[count]+hour_second_count*temp_diff)-ambient_temperature.level
                                   if temp_change >0:
                                          yield ambient_temperature.put(temp_change)
                                   elif temp_change <0:
                                          yield ambient_temperature.get(-temp_change)
                                   #print "ambient temp is", ambient_temperature.level
                                   yield env.timeout(10)
                                   hour_second_count+=10
                            hour_second_count=0
                     count += 1
              
def convection(env,temperature,ambient_temperature):
       #function to model convection from environment to algae bottle using convection formula in physical world
       while True:
              temp_change2 = 10.*heat_transfer_coefficient*(ambient_temperature.level-temperature.level)*area_of_bottle/(mass*heat_capacity)
              #print temp_change2
              if temp_change2 >0:
                     temperature.put(temp_change2)
              if temp_change2 <0:
                     temperature.get(-temp_change2)
              yield env.timeout (10)
                            
              
#Process 2 - removes heat from algae bottle using controller and pump       
def controller(env,temperature):
       #function to read the temperature and call the heat exchanger(pump) if the temperature gets too high
       count=0
       while True:
              Tlist.append(temperature.level)
              count+=1
              #print "algae temperature is", temperature.level
              if count !=1:
                     pwm = k*(temperature.level-threshold)+k2*(Tlist[count-1]-Tlist[count-2])
                     if pwm >99:
                            pwm = 99 #caps the maximum output at 5V
                     temp_change3 = 2.5*pwm*5/(100*mass*heat_capacity)
                     if temp_change3>0:
                            yield temperature.get(temp_change3)
                            yield power_used.put(5*pwm/100) #adding the power used as the pwm output
              yield env.timeout(10)
       
       
#process 3 - adds heat to algae bottle due to solar irradiation
def heat_flux(env,temperature):
       while True:
              count=0
              while count <= 23:
                     hour_second_count=0
                     while hour_second_count < 3600:
                            temp_change4 = hourly_sun_duration[count]*120*area_of_bottle*10./(mass*heat_capacity)
                            #print temp_change4
                            if temp_change4 >0:
                                   yield temperature.put(temp_change4)
                            yield env.timeout(10)
                            hour_second_count+=10
                     count+=1
              count = 0
              

#starting the environment
k_list=[x for x in xrange(1,11)]
power_used_list=[]

for elem in k_list:
       k = elem #the proportional derivative controller's k values
       k2=elem
       Tlist=[] #list of temperature for proportional derivative controller
       env = simpy.Environment()
       temperature=simpy.Container(env,init=25)
       ambient_temperature=simpy.Container(env,init=26.5)
       power_used=simpy.Container(env,init=0)
       env.process(heat_flux(env,temperature))
       env.process(temp_flux(env,ambient_temperature))
       env.process(controller(env,temperature))
       env.process(convection(env,temperature,ambient_temperature))
       
       env.run(until=simtime)
       power_used_list.append(power_used.level)

       plt.plot(xrange(0,simtime,10),Tlist) 
       plt.axis([0,simtime+100,20,40])
       plt.show()
       
       
       
#use this code to plot for power used vs k values
      
#plt.plot(k_list,power_used_list)
#plt.axis([0, 0.001, 0, 10000])
#plt.show()
'''
to solve for the k values, we will need to use different pair of k values and compare their power usage
a greater k value will consume more power, but it will also ensure that the algae bottle reached the 
desired temperature state faster, a smaller k value will use less energy, but will take a longer time 
to reach the desired temperature
'''