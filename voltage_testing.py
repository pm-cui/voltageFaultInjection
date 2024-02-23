import time, sys, uselect
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine
import math

# Set the Gate of the Driver MOSFET to HIGH for a short period, driving the voltage down. Glitches the STM32. (See sketch schematics)
@asm_pio(set_init = rp2.PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
def drop_voltage():
    # Delay and Glitch durations are all inside the 32bit string.
    # Bits 0-4 is used for delay duration (32 cycle loop)
    # Bits 5-9 is used for delay duration (2 cycle loop)
    # Bits 10-14 is used for glitch duration
    pull()
    mov(isr, osr)
    
    # Start of program
    label("Prog_Start")
    
    # Move/Reloads the glitch timing and delay into the x and y registers
    out(x, 5)		#x contains the delay duration (2 cycle loop) 
    out(y, 5)		#y contains the delay duration (32 cycle loop)
    #nop()			#The 5 LSB of OSR should now contain the glitch duration
    
    # Waits for Rising Edge from Pin 4 before glitching with Pin 3
    wait(1, pin, 0)
    
    
    # 2 cycle delay
    label("delay_short")
    nop()		
    jmp(x_dec, "delay_short")
    
    #nop()
    
    # Skips 32 cycle delay and goes to glitch
    jmp(not_y, "Glitch")
    
    # 32 cycle delay
    label("delay_long")
    nop()		[30]
    jmp(y_dec, "delay_long")
    
    label("Glitch")
    # Moves the glitch timing to scratch register X
    mov(x, osr)
    
    # Set Pin 3 to High. Induces Glitch
    set(pins, 1)
    
    # Glitch timing
    label("glitch_timing")
    nop()
    jmp(x_dec, "glitch_timing")
    
    #nop()	

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
    
    # Reloads the original value back into OSR
    mov(osr, isr)
    # Wait for Falling edge so the PIO does not continually glitch
    wait(0, pin, 0)
    jmp("Prog_Start")
    
# Set Pin 3 output drive strength to be 12mA, slew to be fast. Refer to rp2040 datasheet, PADS_BANK0
machine.mem32[0x4001c010]=0x7f

# Open a file from the Pico's onchip flash memory
fd = open("output.txt", "a")

#Start flag
start_flag = 0

# Bit String
bit_string = 0

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
    cycles = 5 + (int(duration) - 160) / 20
    return cycles


def filter(data):
    data = data.replace("i = 10 j = 100 ctrl = 1000 \n\r", '')
    return data


#while True:
for i in range (260, 280, 20): #glitch duration. Accurate to ~20ns
    for j in range(380, 1000, 20): #delay duration. Accurate to ~20ns
        t_end = time.time() + 5
        #fd.write(f"Glitch duration: {i}, Delay Duration {j} \n")
        
        glitch_cycles = calc_glitch_cycles(i)
        bit_string = int(glitch_cycles) << 10		#Logical shift left by 10 bits
        print(glitch_cycles)
        print(f"Glitch duration: {i}")
        print(f"Delay duration: {j}")
        
        if (j < 780):
            #~90ns of delay is due to current travel time(?). Was mentioned before in one of the meetings. 
            delay_cycles = (j - 140 )/20	# At least 4 cycles is being used for delay. 
            bit_string = bit_string + int(delay_cycles)		# No need to shift 2 cycle delay as they are the 5 LSB
        else:
            long_delay_cycles = math.floor((j - 140) / 320) 
            delay_cycles = math.floor((j - (long_delay_cycles *320) - 110 ) / 20) #~90ns of delay + 10ns of delay to copy osr into x
            long_delay_cycles = long_delay_cycles - 1 # Loops in PIO index starts at 0
            delay_cycles = delay_cycles -1
            bit_string = bit_string + (long_delay_cycles << 5)
            bit_string = bit_string + delay_cycles
            print(f"long delay cycle: {long_delay_cycles}")
        print(f"Delay Cycles: {delay_cycles}")
        print(f"Bit_string: {bit_string}")
        
        sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3), in_base = Pin(4))
        sm.put(bit_string)
        sm.active(1)
        start_flag = 1

        while time.time() < t_end:
            # Prints output of STM32 to Thonny IDE
            if uart.any():
                try:
                    # Removes the trailing empty spaces and decodes the string received
                    data = uart.read().decode('ascii').rstrip('\xff').rstrip('\x00')
                    
                    # Prints data to terminal
                    print(data)
                    
                    if (data != "i = 10 j = 100 ctrl = 1000 \n\r"):
                        fd.write(f"Glitch duration: {i}, Delay Duration {j} \n")
                        print("Writing")
                        fd.write(data)
                    
                    # Removes the expected data and only adds abnormal data to the file
                    data = filter(data)
                    if (len(data) > 0):
                        fd.write(f"Glitch duration: {i}, Delay Duration {j} \n")
                        #print("Writing")
                        print(data)
                        fd.write(data)

                except:
                    data = uart.read()
                    print(data)




