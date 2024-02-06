import time, sys, select
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the MOSFET to high for a few clock cycles, causing the output to be 0v. Simulates a drop in voltage
@asm_pio(set_init = rp2.PIO.OUT_LOW)
def drop_voltage():
    
    #Set Pin to High
    set(pins, 1)	
    
    #Delay
    nop()	[15]
    '''
    set(x, 31)
    label("delay_high_outer")
    set(y, 2)
    label("delay_high_inner")
    nop()			[31]
    jmp(y_dec, "delay_high_inner")
    jmp(x_dec, "delay_high_outer")
    '''
    
    #Set Pin to Low
    set(pins, 0)
    
    nop() [31]
    
    #Delay
    set(x, 31)
    label("delay_low_outer")
    set(y, 2)
    label("delay_low_inner")
    nop()			[31]
    jmp(y_dec, "delay_low_inner")
    jmp(x_dec, "delay_low_outer")
    
    
# https://forums.raspberrypi.com/viewtopic.php?t=300735#:~:text=The%20GPIO%20appears%20to%20be,Is%20that%20set%20with%20uPython%3F
# Seach PADS_BANK0 in the rp2040 datasheet, pg 302
# In the pad control register, bits 5:4 control the drive strength. 0x0-> 2mA | 0x1 -> 4mA | 0x2-> 8mA | 0x3 -> 12mA
# 0x4001c000 is the base address. Pin 0 at offset of 0x04, 0x4001c004. Pin 3 offet would be 16, which is 0x010
machine.mem32[0x4001c010]=0x7f

led = Pin("LED", Pin.OUT)
led.value(1)

uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=None, stop=1)

#fd = open("output.txt", "a")

sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3))
sm.active(1)

while True:
    if uart.any():
        data = uart.read().decode('ascii').rstrip('\x00')
        #fd.write(data)
        print(data)

    