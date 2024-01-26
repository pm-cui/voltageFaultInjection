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
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32_Disassembly.png
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

## Current Issues
- Looking at the schematics, JP6 connects the 3v3 output to the MCU. Therefore, I directly connected the 3v3 to the Pin leading to the MCU
- When STM is not connected to the laptop:
  - Pin 32 on the MCU is not receiving power even though Pins 64, 48, 19 are all receiving power correctly.
  - Tx/Rx of data does not work from STM to Pico
- When STM is connected to the laptop:
  - Able to transmit data properly
- When inducing the voltage drop, results are as listed below:
  - Standalone, not connected:-
    - ~100ns rise/fall time 
  - Connected to STM on JP6's Pin:-
    - Steep drop followed by a slow curve. Total time for voltage drop is approximately 5 microseconds. 
    - Likely due to the presence of capacitors. Consider desoldering them from the STM board?
- In the paper Shaping the Glitch, their drop was only took ~50ns. The total glitch time was approximately 200ns. 

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
