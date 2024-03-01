from machine import Pin,UART
import time
import struct
#https://stackoverflow.com/questions/73105957/stm32-memory-dump-and-extracting-secret-key
#https://forum.micropython.org/viewtopic.php?t=9587/1000
# https://github.com/newaetech/chipwhisperer/blob/develop/software/chipwhisperer/hardware/naeusb/programmer_stm32fserial.py#L298 (Line 332, 313)

uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=0, stop=1) #0 for even parity
led = Pin("LED", Pin.OUT)
out1 = Pin(3, Pin.OUT)
out2 = Pin(5, Pin.OUT)

led.value(1)
out1.value(0)
out2.value(0)

# Command to initialize bootloader mode
foo = struct.pack('B', 0x7f)
print(foo)

time.sleep(1)
print("sending")
uart.write(foo)

bar, = struct.unpack('b', uart.read())
print(bar)

while True:
    # Read Memory Command Start

    # Select Read Memory Command
    time.sleep(1)
    foo = struct.pack('B', 0x11)
    uart.write(foo)
    out2.value(1)
    foo = struct.pack('B', 0xee)
    uart.write(foo)

    # Receive ACK or NACK
    bar, = struct.unpack('b', uart.read())
    print(bar)
    out2.value(0)
    if (bar != 121):
        print("test")
        continue

    # Send Start Address + Checksum
    time.sleep(1)
    foo = struct.pack('B', 0x08)
    uart.write(foo)
    foo = struct.pack('B', 0x00)
    uart.write(foo)
    foo = struct.pack('B', 0x00)
    uart.write(foo)
    foo = struct.pack('B', 0x00)
    uart.write(foo)
    foo = struct.pack('B', 0x08)
    uart.write(foo)

    bar, = struct.unpack('b', uart.read())
    print(bar)

    # Send number of bytes to read + Checksum
    time.sleep(1)
    foo = struct.pack('B', 0x0f)
    uart.write(foo)
    foo = struct.pack('B', 0xf0)
    uart.write(foo)

    # Receive ACK/NACK + Memory content
    print(uart.read().hex())
    
    time.sleep(1)



'''
while True:
    try:
        bar, = struct.unpack('b', uart.read())
        print(bar)
    except:
        pass
'''