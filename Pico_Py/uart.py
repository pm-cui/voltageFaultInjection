from machine import Pin,UART
import time
#https://stackoverflow.com/questions/73105957/stm32-memory-dump-and-extracting-secret-key
#https://forum.micropython.org/viewtopic.php?t=9587/1000

uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=None, stop=1)
led = Pin("LED", Pin.OUT)
outp = Pin(3, Pin.OUT)

uart_init = b'\x7f'
read_mem_cmd = b'\x11\xee'

led.value(1)
outp.value(0)

'''
time.sleep(2)
uart.write(hex(127)) #0x7F
time.sleep(1)
uart.write(hex(17))   #0x11
uart.write(hex(238))  #0xEE
print("sent")
'''

while True:
    if uart.any(): 
        data = uart.read() 
