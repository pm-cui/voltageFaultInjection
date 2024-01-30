# PIO Episode 20, Demo 20A
# Demonstrating ID and clearing of IRQ 0 through 4 on one state machine
# Note that IRQ is cleared when handler is started, not completed
# 
from machine import Pin
import rp2
import time

pio_0 = rp2.PIO(0)

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW) # assemble the PIO program
def blink_1hz():
    # Turn on the LED and delay, taking 1000 cycles.
    label("start")
    set(pins, 1)
    set(x, 31)                  [5]
    label("delay_high")
    nop()                       [29]
    jmp(x_dec, "delay_high")
    # Turn off the LED and delay, taking 1000 cycles.
    set(pins, 0)
    set(x, 31)                  [6]
    label("delay_low")
    nop()                       [29]
    jmp(x_dec, "delay_low")
# set interrupt and stall
    label("irq_stall")
    irq(block,0 )
    jmp('start')                

def my_handler(sm):  #Interrupt handler
    x=(rp2.PIO(0).irq().flags()) # Get value of INTS Register
    print(time.ticks_ms(), 'rp2.PIO(0).irq():',x,'= {:#014b}'.format(x))

rp2.PIO(0).irq(handler = my_handler) #Assign the handler to the PIO block
    
# Create StateMachine(0) with the blink_1hz program, outputting on Pin(0).
sm_0 = rp2.StateMachine(0, blink_1hz, freq=2000, set_base=Pin(0)) #, jmp_pin=BLINK_OFF_PIN_0)
sm_0.active(1)

# Just chill while PIO keeps interrupting
while True:
    time.sleep(2)