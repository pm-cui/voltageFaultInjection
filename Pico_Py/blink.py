import machine
import time

led_pin = machine.Pin(25, machine.Pin.OUT)
#pow_pin = machine.Pin(2, machine.Pin.OUT)
gate_pin = machine.Pin(3, machine.Pin.OUT)
#pow_pin.value(1)

#while True:
t_end = time.time() + 10
while time.time() < t_end:
    led_pin.value(1)
    time.sleep(1)
    led_pin.value(0)
    time.sleep(1)
    '''    
    led_pin.value(1) #turn on LED
    gate_pin.value(1)
    utime.sleep(3)
    
    led_pin.value(0)
    gate_pin.value(0)
    utime.sleep(3)
    '''