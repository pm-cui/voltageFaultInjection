import time, sys, select
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

#Set the Gate of the MOSFET to high for a few clock cycles, causing the output to be 0v. Simulates a drop in voltage
# autopull: Automatically refills the OSR from the FIFO on an OUT instruction, once the threshhold is met.
# PULL: REMOVES a 32-bit word from the TX FIFO and places it into the OSR
# OUT shifts data from OSR to other destination. OSR changes
# IN shifts data from pin/registers to ISR. Original register does not change
@asm_pio(set_init = rp2.PIO.OUT_LOW, autopull = True, out_shiftdir = PIO.SHIFT_RIGHT, pull_thresh = 10)
def drop_voltage():

    pull()
    mov(x, osr)
    out(y,4)
    mov(isr, y)
    push()
    out(isr, 4)
    push()
    mov(isr, osr)
    push()
    mov(osr, x)
    
    
    
    
    
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

sm = StateMachine(0, drop_voltage, freq = 2_000, set_base = Pin(3))
sm.put(1000)
sm.active(1)


while True:
    data = sm.get()
    print(data)
    

    