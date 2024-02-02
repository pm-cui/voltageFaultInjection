from machine import Pin,UART
import time
#https://stackoverflow.com/questions/73105957/stm32-memory-dump-and-extracting-secret-key
#https://forum.micropython.org/viewtopic.php?t=9587/1000
# https://github.com/newaetech/chipwhisperer/blob/develop/software/chipwhisperer/hardware/naeusb/programmer_stm32fserial.py#L298 (Line 332, 313)

uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=0, stop=1) #0 for even parity
led = Pin("LED", Pin.OUT)
outp = Pin(3, Pin.OUT)

uart_init = b"\x7F"
read_mem_cmd = b'\x11\xee'

led.value(1)
outp.value(1)


while True:
    time.sleep(1)
    print(f"Sending {uart_init}")
    uart.flush()
    time.sleep(0.5)
    uart.write(uart_init)

    if uart.any(): 
        data = uart.read()
