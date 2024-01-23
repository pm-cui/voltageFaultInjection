import time, sys, uselect
from machine import Pin
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the MOSFET to high for a few clock cycles, causing the output to be 0v. Simulates a drop in voltage
@asm_pio(set_init = rp2.PIO.OUT_LOW)
def drop_voltage():
    #Set Pin to High
    set(pins, 1)
    
    #Delay
    set(x, 31)
    label("delay_high_outer")
    set(y, 2)
    label("delay_high_inner")
    nop()			[31]
    #nop()			[31]
    jmp(y_dec, "delay_high_inner")
    jmp(x_dec, "delay_high_outer")

    
    #Set Pin to Low
    set(pins, 0)
    
    #Delay
    set(x, 31)
    label("delay_low_outer")
    set(y, 2)
    label("delay_low_inner")
    nop()			[31]
    jmp(y_dec, "delay_low_inner")
    jmp(x_dec, "delay_low_outer")
    
#Switches the on-board LED to ON state.
led = Pin("LED", Pin.OUT)
led.value(1)

#Sets up the comms btw Pico and Thonny IDE
spoll=uselect.poll()
spoll.register(sys.stdin,uselect.POLLIN)

def read1():
    return(sys.stdin.read(1) if spoll.poll(0) else None)

def readline():
    c = read1()
    buffer = ""
    while c != None:
        buffer += c
        c = read1()
    return buffer

def get_freq():
    print("Enter Frequency (Hz): ", end = "")
    while True:
        freq_input = readline()
        if len(freq_input) != 0:
            try:
                #PIO can run from 2000Hz to 133Mhz. Reject any other values. 
                if (int(freq_input) < 2000 or int(freq_input) > 125000000):
                    raise Exception
                
                return freq_input
                
            except:
                print("Error, please enter an integer between 2000 and 125,000,000.")
                print("Enter Frequency (Hz): ", end = "")

while True:
    frequency = get_freq()
    sm = StateMachine(0, drop_voltage, freq = int(frequency), set_base = Pin(3))
    print("Frequency: " + frequency)
    sm.active(1)





'''
#Get user input to control the frequency and time of voltage drop of the StateMachine
print("Enter Frequency (Hz): ", end = "")
while True:
    freq_input = readline()
    if len(freq_input) != 0:
        try:
            #PIO can run from 2000Hz to 133Mhz. Reject any other values. 
            if (int(freq_input) < 2000 or int(freq_input) > 125000000):
                raise Exception
            
            sm = StateMachine(0, drop_voltage, freq = int(freq_input), set_base = Pin(3))
            print("Frequency: " + freq_input)
            sm.active(1)
            
            
        except:
            print("Error, please enter an integer between 2000 and 125,000,000.")
            print("Enter Frequency (Hz): ", end = "")
'''
