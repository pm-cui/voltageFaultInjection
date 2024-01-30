import time, sys, select
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the MOSFET to high for a few clock cycles, causing the output to be 0v. Simulates a drop in voltage
@asm_pio(set_init=PIO.OUT_LOW)
def drop_voltage():
    wait(1, pin, 0)
    set(pins, 1)
    wait(0, pin, 0)
    set(pins, 0)

    
    
    

led = Pin("LED", Pin.OUT)
led.value(1)

uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=None, stop=1)


sm = StateMachine(0, drop_voltage, freq = 2_000, set_base = Pin(3), in_base = Pin(4))
sm.active(1)

while True:
    if uart.any(): 
        data = uart.read()
        print(data)
