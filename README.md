# Voltage Fault Injection
- Develop a fault injector hardware prototype using a low-cost development board (Raspberry Pi Pico)
- Execute fault injection using the developed fault injector against different products
- Study why some products are more susceptible to fault injections by extracting the MCU ROM code to identify possible failure points.


## Current Goal
- STM32 is running an infinite loop and a conditional statement that will never be reached
- Using the Pico, conduct VFI to corrupt the data and break into the conditional statement
- Make a terminal UI to allow users to input the frequency to run the PIO at and the duration of the glitch.
   

## Progress
### Raspberry Pi Pico (using micropython and asm_PIO)
- Main Program
  - Prompt user to input the frequency of the State Machine (once at the start of the program). Might changed this to make the Pico run at a standard 100Mhz later on.
  - After getting a valid input, runs the State Machine. (refer to PIO)
  - Prompts user to input the duration of the glitch (Repeated)
  
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low.
  - autopull = False -> Does not automatically refill the OSR with the value from the TX FIFO. This causes the PIO to wait for user input before causing the glitch.
  - Waits for user input from the main program to be written to the TX FIFO before causing the glitch.
  - Causes GPIO to be asserted for a short amount of time before turning returning to a low state

### STM32 Nucleo-F103RB
- Runs an infinite loop, counting from 0 to 3.
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32_Disassembly folder. 
- Manipulation of register values is also present in the STM32_Disassembly folder.
- Outputs via USB to laptop's terminal (Subjected to change due to capacitors)
- JP5's Jumper to connect the 2 leftmost Pins. This causes the ST-Link component to not be powered and the board can then operate in 3v3. 
- JP6 connects the power supply to the MCU (U5). Removing jumper from JP6 will result in the MCU to turn off.
- Therefore, I removed the jumper and directly connected the 3v3 directly to the Pin leading to the MCU. However there are issues. (Stated below)
- STM is still able to transmit over to laptop

### P&N MOSFET
- Connection of MOSFET is akin to Pull-up/Pull-down resistors.
- Acts as switches to power and ground the STM32.
- Current connection schematics (in word form):
  - 3V3 from Pico -> PS1
  - GPIO 3 from Pico -> PG1
  - PD1 -> STM32 AND ND1
  - NG1 -> GPIO 3 from Pico
  - NS -> Ground
- When GPIO Pin 3 is OFF:
  - P-Channel MOSFET allows current to flow from SOURCE(3V3) to DRAIN(STM) (Switch is closed)
  - N-Channel MOSFET prevents current flow from DRAIN(STM) to SOURCE(GROUND) (Switch is opened)
  - Power is supplied to STM32 while the switch to Ground is open. 
- When GPIO Pin 3 is ON:
  - P-Channel MOSFET prevents current flow from SOURCE(3V3) to DRAIN(STM) (Switch is opened)
  - N-Channel MOSFET allows current to flow from DRAIN(STM) to SOURCE(GROUND) (Switch is closed)
  - Power is cut to the STM32 and current flows from STM to Ground.
 
### Driver MOSFET
- Acts as a Pull-up Resistor.
- When Pin 3's output is 0, Driver MOSFET's Gate is open and voltage is supplied to PG1 and NG1. P-Channel MOSFET is opened and no voltage is supplied to STM.
- When Pin 3's output is 1, Driver MOSFET's Gate is closed and causes the circuit to short to GRD, causing PG1 and NG1 to not be powered. P-channel MOSFET is closed and N-Channel MOSFET is opened and voltage is supplied to STM.

## Current Issues
- When STM is not connected to the laptop via ST-Link:
  - Pin 32 on the MCU is not receiving power even though Pins 64, 48, 19 are all receiving power correctly.
  - Tx/Rx of data does not work from STM to Pico
  - STM's GPIO also does not work
  - USB Adaptor also does not work
    
- When STM is connected to the laptop:
  - Able to transmit data properly
  - GPIO works
 
- When JP6's jumper is attached and power is supplied via 3v3, GPIO works as per normal.
   - Can consider desolering capaitors on the side of SB2

## Results of Current Setup
- Note: In the paper Shaping the Glitch, their drop was only took ~50ns. The total glitch time was approximately 200ns.
  
### No driver MOSFET, not connected to STM
- Rise time: ~100ns, Fall time: ~100ns

### Driver MOSFET, Not connected to PG1 and NG1, using 220 Ohms resistor
- Rise time: ~50ns, Fall time: ~20ns

### Driver MOSFET, Not connected to PG1 and NG1, using 10k Ohms resistor
- Rise time: ~2 microseconds, Fall time: ~20ns

### Driver MOSFET, Connected to PG1 and NG1, using 220 Ohms resistor
- Rise time: ~1.5 microseconds, Fall time: ~150ns

### Driver MOSFET, Connected to PG1 and NG1, using 220 Ohms resistor, Connected to STM32's JP6
- Rise time: ~6 microseconds, Fall time: ~6 microseconds

### Driver MOSFET, Connected to PG1 and NG1, using 220 Ohms resistor, Connected to STM32's JP6 w ST-Link connected to laptop
- Rise time: ~10 microseconds, Fall time: ~10 microseconds



## To Do:
### Raspberry Pi Pico
- Glitch timing from user input is not yet accurate as of now. Will work on it after getting a glitch correctly. For now, I have to manually change the timing of the glitch.
- Probably will have to run some calculations on how many cycles the GPIO Pins should be asserted for
- Nested for loop is available. 4 Registers can be used: OSR, ISR, x, y
- Implement a 1s delay between glitches by using pull(asm), sm.put(), time.sleep. 

### STM32 Nucleo-F103RB
- Figure out the locations of the capacitors and consider removing them
- Desolder or look into ways to bypass the capacitors on the STM to induce a much faster voltage drop. 

### MOFSET
- Verify if the connections are correct

## Future Goals
- Dump the STM32's memory to terminal using VFI.
- Currently after looking at the documentation for the STM32:
  - Boot0 Pin should be set to 1, Boot1 Pin should be set to 0. This pattern will enable bootloader mode. (found in pg 75 of AN2606)
  - Press the reset button on the STM32 board
  - Send 0x7F on any one of the 3 USART pins to configure that USARTx Pins. 
  - In bootloader mode, the STM32 takes in various commands through the USARTx Pins, notably the Read Memory Command. (found in pg 15 of AN3155)
  - Following the flowchart present on pg 16, a glitch should be sent after the byte-string is sent to STM to skip the Read Protection and cause it to dump specified blocks of memory.
- As of now:
   - Able to enter bootloader mode(?)
   - Looking into sending data through the USART to use the Bootloader Commands. uart.write(hex(127)) (0x7F) does not work as of now
