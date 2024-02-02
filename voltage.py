import time, sys, uselect
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the Driver MOSFET to LOW for a short period. Glitches the STM32. (See sketch schematics)
@asm_pio(set_init = rp2.PIO.OUT_HIGH, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
def drop_voltage():
    #Get the glitch timing from the OSR (not in use right now)
    pull()
    
    #Waits for Rising Edge from Pin 4 before glitching with Pin 3
    wait(1, pin, 0)
    
    #Can include some waiting time before glitch occurs
    #nop()			[10]
    
    #Set Pin 3 to Low. Induces Glitch
    set(pins, 0)
    
    #Delay. Include the proper cycles later on
    set(x, 3)
    label("delay_low_outer")
    set(y, 0)
    label("delay_low_inner")
    nop()			[31]
    jmp(y_dec, "delay_low_inner")
    jmp(x_dec, "delay_low_outer")
    
    #in between 7-10
    nop()	[10]

    
    #Set Pin 3 to High. Return opertaions as per normal
    set(pins, 1)
    
    #Delay=
    set(x, 31)
    label("delay_high_outer")
    set(y, 31)
    label("delay_high_inner")
    nop()			[31]
    jmp(y_dec, "delay_high_inner")
    jmp(x_dec, "delay_high_outer")
    
    #Wait for Falling edge so the PIO Does not continually glitch
    wait(0, pin, 0)
    
#Switch ON the on-board LED.
led = Pin("LED", Pin.OUT)
led.value(1)

#Initialize UART
#When connected in Normal operation, parity = None
#When connected in Bootloader mode, partity = 0 (EVEN)
uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=None, stop=1)

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
                
def get_glitch_duration():
    print("Enter glitch duration(ns): ", end = "")
    while True:
        glitch_duration = readline()
        if len(glitch_duration) != 0:
            try:
                #GLitch duration to be determined later. According to research, should be approximately 200ns-ish
                if (int(glitch_duration) < 1 or int(glitch_duration) > 30):
                    raise Exception
                
                return glitch_duration
                
            except:
                print("Error, please enter an integer between 1 and 30.")
                print("Enter glitch duration(ns): ", end = "")

#Get user input for the glitch duration
print("State Machine's Frequency is set to 100Mhz")
glitch_time = get_glitch_duration()

#Set up the State Machine and puts the glitch timing to the OSR of the State Machine
sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3), in_base = Pin(4))
sm.put(glitch_time)
sm.active(1)

while True:
    #Prints output of STM32 to Thonny IDE
    if uart.any(): 
        data = uart.read()
        print(data)
