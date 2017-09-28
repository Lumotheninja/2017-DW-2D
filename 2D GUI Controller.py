# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 14:54:09 2017

@author: James
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button 
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.textinput import TextInput
from libdw import sm
from time import sleep

class TemperatureController(App):
    def build(self):
        self.layout = GridLayout(cols=2)

        self.controller = Controller()

        
        ###
        targtemp = Label(text = 'Target Temperature',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(targtemp)
        
        self.tt = TextInput(text = '30.0', font_size = 24, multiline = False)
        self.layout.add_widget(self.tt)
        ###
        
        ###
        sys_temp = Label(text = 'System Temperature',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(sys_temp)
        
        self.sys_temp_val = Label(text = '30.0',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(self.sys_temp_val)
        ###


        ###
        pumpoutput = Label(text = 'Pump Speed',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(pumpoutput)

        self.pumpspeed = Label(text = '0.0',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(self.pumpspeed)
        ###
        

        
        ###
        fanoutput = Label(text = 'Fan Speed',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(fanoutput)

        self.fanspeed = Label(text = '0.0',font_size=24,halign='left',valign='middle')
        self.layout.add_widget(self.fanspeed)
        ###
        
        
        ###
        increase5 = Button(text='+0.5', on_press = self.changetempin5, font_size=24)
        self.layout.add_widget(increase5)
        
        decrease5 = Button(text='-0.5', on_press = self.changetempde5, font_size=24)
        self.layout.add_widget(decrease5)
        ###
        
        
        ###
        increase1 = Button(text='+0.1', on_press = self.changetempin1, font_size=24)
        self.layout.add_widget(increase1) 
        
        decrease1 = Button(text='-0.1', on_press = self.changetempde1, font_size=24)
        self.layout.add_widget(decrease1)
        ###
            
        return self.layout

        
    def changetempin5(self,instance):
        print 'press'
        self.sys_temp_val.text = str(float(self.sys_temp_val.text) + 0.5)
        self.controller.limit = float(self.tt.text)
        self.pumpspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[0])
        self.fanspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[1])

    def changetempde5(self,instance):
        print 'press'
        self.sys_temp_val.text = str(float(self.sys_temp_val.text) - 0.5)
        self.controller.limit = float(self.tt.text)
        self.pumpspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[0])
        self.fanspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[1])

    def changetempin1(self,instance):
        print 'press'
        self.sys_temp_val.text = str(float(self.sys_temp_val.text) + 0.1)
        self.controller.limit = float(self.tt.text)
        self.pumpspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[0])
        self.fanspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[1])

    def changetempde1(self,instance):
        print 'press'
        self.sys_temp_val.text = str(float(self.sys_temp_val.text) - 0.1)
        self.controller.limit = float(self.tt.text)
        self.pumpspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[0])
        self.fanspeed.text = str(self.controller.step(float(self.sys_temp_val.text))[1])


class Controller(sm.SM):
    state = 0
    def getNextValues(self,state,inp):
        self.error = inp - self.limit
        
        try:
            self.diff =0 #(self.error - self.prev) / 2.2 because its not real
        except AttributeError:
            self.diff = 0
        
        self.prev = self.error
        
        Kp = [10,10]
        Kd = [-0.1,-0.1]
        
        if state == 0 and inp < self.limit:
            nextState = 0
            return (nextState,(0.0,0.0))
            
        elif state == 0 and inp >= self.limit:
            nextState = 1
            ########## PID CONTROLLER##############

            pwm_fan = Kp[0] * self.error + Kd[0] * self.diff
            pwm_pump = Kp[1] * self.error + Kd[1] * self.diff
            #####limit pwm Between 0 to 100 duty cycle#####
            if pwm_fan > 90:
                pwm_fan = 90.0
            if pwm_fan < 0:
                pwm_fan = 0.0               
            if pwm_pump > 90:
                pwm_pump = 90.0
            if pwm_pump < 0:
                pwm_pump = 0.0
            return (nextState,(pwm_fan,pwm_pump))
            
        elif state == 1 and inp < self.limit:
            nextState = 0
            return (nextState,(0.0,0.0))
            
        elif state == 1 and inp >= self.limit:
            nextState = 1
            pwm_fan = Kp[0] * self.error + Kd[0] * self.diff
            pwm_pump = Kp[1] * self.error + Kd[1] * self.diff
            #####limit pwm Between 0 to 100 duty cycle#####
            if pwm_fan > 90:
                pwm_fan = 90.0
            if pwm_fan < 0:
                pwm_fan = 0.0               
            if pwm_pump > 90:
                pwm_pump = 90.0
            if pwm_pump < 0:
                pwm_pump = 0.0
            return (nextState,(pwm_fan,pwm_pump))

TemperatureController().run()