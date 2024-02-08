import time, sys, uselect
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

# Set the Gate of the Driver MOSFET to HIGH for a short period, driving the voltage down. Glitches the STM32. (See sketch schematics)
@asm_pio(set_init = rp2.PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
def drop_voltage():
    # Get the glitch timing and store it in the ISR
    pull()
    mov(isr, osr)
    
    # Get the delay and leave it in the OSR
    pull()
    
    label("Prog_Start")
    
    # Move/Reloads the glitch timing and delay into the x and y registers
    mov(x, isr)		#x contains glitch timing
    mov(y, osr)		#y contains delay duration
    
    # Waits for Rising Edge from Pin 4 before glitching with Pin 3
    wait(1, pin, 0)
    
    # Delay duration
    label("delay_duration")
    nop()		
    jmp(y_dec, "delay_duration")
    
    # Set Pin 3 to High. Induces Glitch
    set(pins, 1)
    
    # Glitch timing
    label("glitch_timing")
    nop()
    jmp(x_dec, "glitch_timing")
    
    # Set Pin 3 to Low. Return opertaions as per normal
    set(pins, 0)
    
    # Delay to allow the STM to get back to operating voltage
    set(x, 31)
    label("delay_low_outer")
    set(y, 2)
    label("delay_low_inner")
    nop()			[31]
    jmp(y_dec, "delay_low_inner")
    jmp(x_dec, "delay_low_outer")
    
    
    # Wait for Falling edge so the PIO does not continually glitch
    wait(0, pin, 0)
    jmp("Prog_Start")
    
# Set Pin 3 output drive strength to be 12mA, slew to be fast. Refer to rp2040 datasheet, PADS_BANK0
machine.mem32[0x4001c010]=0x7f

# Open a file from the Pico's onchip flash memory
fd = open("output.txt", "a")

#Start flag
start_flag = 0

# Switch ON the on-board LED.
led = Pin("LED", Pin.OUT)
led.value(1)

# Initialize UART
# When connected in Normal operation, parity = None
# When connected in Bootloader mode, partity = 0 (EVEN)
uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=None, stop=1)

# Sets up the comms btw Pico and Thonny IDE
spoll=uselect.poll()
spoll.register(sys.stdin,uselect.POLLIN)

def read1():
    return(sys.stdin.read(1) if spoll.poll(0) else None)

def readline():
    c = read1()
    buffer = ""
    while c != None:
        buffer += c
        c = read1()
    return buffer
                
def get_glitch_duration():
    print("Glitch timing is accurate to 20ns")
    print("Enter glitch duration(ns) btw 160 to 700: ", end = "")
    while True:
        glitch_duration = readline()
        if len(glitch_duration) != 0:
            try:
                # GLitch duration to be determined later. According to research, should be approximately 200ns-ish
                if (int(glitch_duration) < 160 or int(glitch_duration) > 700):
                    raise Exception
                if (int(glitch_duration) % 10 != 0):
                    raise Exception
                
                return glitch_duration
                
            except:
                print("Error, please enter an integer of multiple 10 between 160 and 700.")
                print("Enter glitch duration(ns): ", end = "")

def get_delay_duration():
    print("Enter delay duration(ns) btw 0 to 640: ", end = "")
    while True:
        delay_duration = readline()
        if len(delay_duration) != 0:
            try:
                # GLitch duration to be determined later. According to research, should be approximately 200ns-ish
                if (int(delay_duration) < 0 or int(delay_duration) > 640):
                    raise Exception
                if (int(delay_duration) % 10 != 0):
                    raise Exception
                
                return delay_duration
                
            except:
                print("Error, please enter an integer of multiple 10 between 160 and 600.")
                print("Enter delay duration(ns): ", end = "")

def calc_glitch_cycles(duration):
    #nop() [11] gives a reliable glitch time of 160ns. Each extra clock cycle adds 10ns.
    cycles = 4 + (int(duration) - 160) / 20
    return cycles


def filter(data):
    data = data.replace("i = 0 j = 0 ctrl = 1 \n\r", "")
    data = data.replace("i = 0 j = 1 ctrl = 2 \n\r", "")
    data = data.replace("i = 1 j = 0 ctrl = 3 \n\r", "")
    data = data.replace("i = 1 j = 1 ctrl = 4 \n\r", "")
    return data


for i in range (27, 9, -1):
    for j in range(0, 6):
        #Run each cycle for 30sec
        t_end = time.time() + 60*2
        fd.write(f"Glitch cycle {i}, delay cycle {j} \n")
        
        sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3), in_base = Pin(4))
        sm.put(i)
        sm.active(1)
        sm.put(j)
        start_flag = 1

        while time.time() < t_end:
            # Prints output of STM32 to Thonny IDE
            if uart.any():
                try:
                    # Removes the trailing empty spaces and decodes the string received
                    data = uart.read().decode('ascii').rstrip('\xff').rstrip('\x00')
                    
                    # Prints data to terminal
                    print(data)
                    
                    # Removes the expected data and only adds abnormal data to the file
                    data = filter(data)
                    if (len(data) > 0):
                        fd.write(data)

                except:
                    data = uart.read()
                    print(data)

