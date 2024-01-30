import time, sys, select
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the MOSFET to high for a few clock cycles, causing the output to be 0v. Simulates a drop in voltage
@asm_pio(set_init = rp2.PIO.OUT_LOW)
def drop_voltage():
    #Set Pin to High
    set(pins, 1)
    
    #Delay
    set(x, 31)
    label("delay_high_outer")
    set(y, 0)	
    label("delay_high_inner")
    nop()			[31]
    jmp(y_dec, "delay_high_inner")
    jmp(x_dec, "delay_high_outer")

    
    #Set Pin to Low
    set(pins, 0)
    
    #Delay
    set(x, 31)
    label("delay_low_outer")
    set(y, 0)
    label("delay_low_inner")
    nop()			[31]
    jmp(y_dec, "delay_low_inner")
    jmp(x_dec, "delay_low_outer")
    
    
    

led = Pin("LED", Pin.OUT)
led.value(1)

uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=None, stop=1)


sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3))
sm.active(1)

while True:
    if uart.any(): 
        data = uart.read()
        print(data)
    