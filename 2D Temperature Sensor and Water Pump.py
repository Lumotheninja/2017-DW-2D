from libdw import sm
import os
import glob
import time
import RPi.GPIO as GPIO


###           CONFIGURING THE TEMPERATURE SENSOR               ###

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


###           DEFINING AND SETTING THE GPIO PINS               ###

GPIO.setmode(GPIO.BCM)

pwm_pin = 18
in1_pin = 23
in2_pin = 24
#fan_pin = ##

GPIO.setup(pwm_pin, GPIO.OUT)
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)

p = GPIO.PWM(pwm_pin, 200) #instantiate PWM instance


###           FUNCTIONS                  ###

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp = float(temp_string) / 1000.0
        return temp

        
class Controller(sm.SM):
       state=0
       def getNextValues(self,state,inp):
              if state == 0 and inp < limit:
                     nextState = 0
                     return (nextState,(0.0,0.0))
              elif state == 0 and inp >= limit:
                     nextState = 1
                     return (nextState,(1.0,1.0))
              elif state == 1 and inp < limit:
                     nextState = 0
                     return (nextState,(0.0,0.0))
              elif state == 1 and inp >= limit:
                     nextState = 1
                     return (nextState,(1.0,1.0))

                     
def clockwise():
    GPIO.output(in1_pin, True)    
    GPIO.output(in2_pin, False)

 
def counter_clockwise():
    GPIO.output(in1_pin, False)
    GPIO.output(in2_pin, True)


def pumpcontrol(input):
    if input == 1.0:
        p.start(75)
        clockwise()
    elif input == 0.0:
        p.stop()


def fancontrol(input): #assume fan is powered by GPIO
    if input == 1.0:
        GPIO.output(fan_pin, True)
    elif input == 0.0:
        GPIO.output(fan_pin, False)

                    
tempcon = Controller()
limit=25

while True:
    instr = tempcon.step(read_temp())
    print read_temp(),instr
#    fancontrol(instr[0])
    pumpcontrol(instr[1])

    
