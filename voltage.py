import time, sys, uselect
from machine import Pin
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the MOSFET to high for a few clock cycles, causing the output to be 0v. Simulates a drop in voltage
@asm_pio(set_init = rp2.PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_RIGHT, autopull=False, pull_thresh=16)
def drop_voltage():
    #Waits for user input and determines the duration of the glitch
    pull(block)
    
    #Set Pin to High
    set(pins, 1)
    mov(y, osr)
    
    #Delay
    set(x, 31)
    label("delay_high_outer")
    mov(y, osr)
    label("delay_high_inner")
    nop()			
    jmp(y_dec, "delay_high_inner")
    jmp(x_dec, "delay_high_outer")

    
    #Set Pin to Low
    set(pins, 0)
    
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
                
def get_glitch_duration():
    print("Enter glitch duration(ns): ", end = "")
    while True:
        glitch_duration = readline()
        if len(glitch_duration) != 0:
            try:
                #PIO can run from 2000Hz to 133Mhz. Reject any other values. 
                if (int(glitch_duration) < 1 or int(glitch_duration) > 30):
                    raise Exception
                
                return glitch_duration
                
            except:
                print("Error, please enter an integer between 10 and 30.")
                print("Enter glitch duration(ns): ", end = "")

frequency = get_freq()
sm = StateMachine(0, drop_voltage, freq = int(frequency), set_base = Pin(3))
print("Frequency: " + frequency)
sm.active(1)

while True:
    glitch_time = get_glitch_duration()
    print("Glitching...")
    sm.put(int(glitch_time))
