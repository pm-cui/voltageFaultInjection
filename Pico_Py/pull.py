# Example of using PIO writing a parallel byte from data
# for a more wrapped-up examples, see https://github.com/raspberrypi/pico-micropython-examples/blob/master/pio/pio_pwm.py
#https://www.youtube.com/watch?v=boXSdDnHaAE (bootloader stm)

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

@asm_pio(set_init=rp2.PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_RIGHT, autopull=False, pull_thresh=16)
def paral_prog():
    pull(block) 
    mov(isr, osr)
    mov(x, osr)
    
    #Set Pin to High
    set(pins, 1)
    
    #Delay
    label("delay_high_outer")
    set(y, 2)
    label("delay_high_inner")
    nop()			[31]
    jmp(y_dec, "delay_high_inner")
    jmp(x_dec, "delay_high_outer")

    
    #Set Pin to Low
    set(pins, 0)
    
    #Delay
    mov(x, isr)
    label("delay_low_outer")
    set(y, 2)
    label("delay_low_inner")
    nop()			[31]
    jmp(y_dec, "delay_low_inner")
    jmp(x_dec, "delay_low_outer")

paral_sm = StateMachine(0, paral_prog, freq=2000, set_base=Pin(3))
paral_sm.active(1)

paral_sm.put(31)
sleep(5)
paral_sm.put(31)


'''
while True:
    for i in range(31):
        paral_sm.put(i)
        print(i)
        sleep(1 )
'''