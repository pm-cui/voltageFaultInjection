# Voltage Fault Injection
- Develop a fault injector hardware prototype using a low-cost development board (Raspberry Pi Pico)
- Execute fault injection using the developed fault injector against different products
- Study why some products are more susceptible to fault injections by extracting the MCU ROM code to identify possible failure points.

## Nagivation
- main.c --> STM32's main program code
- STM32 Disassmebly Folder --> Screenshots of STM32's Disassembly window and register manipulation
- voltage.py --> Main code for pico. Contains the main program and PIO code
- Pico_Py folder --> Test codes for the various building blocks
- hello.bin -> binary file downloaded from STM32CubeIDE
- Circuit & waveform sketches are currently done on paper

## Current Goal
- STM32 is running an infinite loop and a conditional statement that will never be reached
- Using the Pico, conduct VFI to corrupt the data and break into the conditional statement
- Make a terminal UI to allow users to input the duration of the glitch. 
   
## Progress
### Raspberry Pi Pico (using micropython and asm_PIO)
- Main Program 
  - State Machine running at a set 100Mhz
  - GPIO set to have a drive strength of 12mA and high slew (default was set to 4mA and low slew)
  - Prompts user for glitch and delay durations
  - After getting a valid input, runs the State Machine
  - Able to press the ENTER key at run time to change the glitch and duration timings
  - Functions avail to convert user input to asm clock cycles, accurate to ~20ns. (look at issues)
     - This accuracy should be fine as Shaping The Glitch also has approximately the same accuracy   
  - Will filter out abnormal outputs and append them to a file. The file resides in the Pico's flash memory
  - Can view the abnormality file using fileoutput.py
  - voltage_testing.py automates the testing of VFI
  - Delay can now go up to ~20,000ns
     - Although registers are 32 bits, only 5 data bits are present, and instructions can work with integers <=32, although the full 32 bit register can be used
     - 2 shift registers and 2 scratch registers present
     - Pass in a bit string containing the glitch duration and delay duration to the TX FIFO
        - Bits 0-4: Number of cycles for short delay (2 cycles per loop)
        - Bits 5-9: Number of cycles for long delay (32 cycles per loop)
        - Bits 10-14: Number of cycles for glitch
        - Utilizing OUT instruction, able to store glitch and delay durations.
  
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low
  - Initializes Pin 4 to be the input pin, getting input from PA10 of the STM32
  - Gets Glitch and Delay durations using the ISR to shift bits out.
  - Upon a rising edge detected on Pin 4:
     - Delays for the number of clock cycles stated in the ISR
     - Sets Pin 3 High for the number of clock cycles stated in OSR
     - Sets Pin 3 Low for a small period of time before waiting for a falling edge. (prevents continous glitching)
 
- voltage_testing.py
   - Slight change to voltage.py:
      - Automates the process of changing the delay and glitch durations
      - Outputs any abnormal data to an output file

### STM32 Nucleo-F103RB
- Runs a loop counting from 0 to 1000
- Toggles PA10. 
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32_Disassembly folder.
- If the if statement is entered, the STM enters an infinite loop and there will be no Tx/Rx of data
- SB12 (remove connection to NRST, which was pulling down the voltage of the MCU), C23, C24, C27, C28, C29 has been removed. Looking to remove c30.
- JP5, JP6 removed jumpers.
- CN2's Jumpers can be removed. Doing so allows the use of the ST-Link v2 to program other STM32 boards.
- Now runs at 4Mhz

### STM32 Nucleo-F103RB (with ST-Link component cut off)
- Conection to ST-Link are as follows:
   - Boot 0 (CN7 Pin 7) to GRD
   - 3v3 to Pico's 3v3
   - VIN to ST-Link CN4 Pin 1
   - CN7 Pin 15 to ST-Link CN4 Pin 2
   - GND to ST-Link CN4 Pin 3
   - CN7 Pin 13 to ST-Link CN4 Pin 4
   - NRST to ST-Link CN Pin 5

### P&N MOSFET
- Driver MOSFET Removed. Using Driver MOSFET increases the rise and fall times. 
- Connection of MOSFET is akin to Pull-up/Pull-down resistors.
- Acts as switches to power and ground the STM32

### Ghidra
- STM32 is a Bare Metal system, application runs directly on the hardware
- Memory-mapped peripherals, Check datasheet of the processor for memory map ***
- Followed along with the video and used Ghidra to analyze the given firmware files
- Downlaoded the bin file from the stm32cubeide to start analyzing the disassembly
- Did some basic analysis on hello.bin 

## Current Issues 

### STM32
- Differences between cutoff board and non-cutoff board:
   - C30 removed (AVDD). 
   - R33 removed (Boot 0). Need to connect it to ground to get out of bootloader mode
   - SB2 removed (Connection to JP6. Should not matter to my board as removed JP6's jumper and directly connecting to its pin)
- The cut-off board is able to glitch from 3v3 to 0 to 3v3. The full board does not drop to 0v even with incresing the glitch timings


### Force resetting of STM
- Tried 2 methods: Using MOSFET to short the 3v3 to ground | Reset the pico using machine.reset()
- MOSFET does not fully short to ground
- machine.reset() causes the pico to disconnect from Thonny IDE and sotp execution
  
## To Do:

### Variables affecting Glitching
- Test various factors known to affect VFI and note their effect. These include:
   - Temperature
   - Clock speed
   - Glitch Duration
   - Glitch Waveform

### Firmware Analysis
- Research on the basics of firmware analysis
- Links used so far:
   -    https://book.hacktricks.xyz/hardware-physical-access/firmware-analysis
   -    https://www.youtube.com/watch?v=zs86OYea8Wk&t=553s
   -    https://www.youtube.com/watch?v=hevWfbWOIew 
   -    https://www.tarlogic.com/blog/owasp-fstm-stage-3-analyzing-firmware/
   -    https://roman1.gitbook.io/blog/embedded-device-exploitation/introduction-to-firmware-analysis
   -    ** https://www.youtube.com/watch?v=q4CxE5P6RUE ** Bare-metal ARM firmware reverse engineering with Ghidra and SVD Loader (The video uses STM32F446RE)
- Download Ghidra and SVD loader and analyze firmware in the video

## Future Goals
- Dump the STM32's memory to terminal using VFI.
- Do firmware analysis on the extracted firmware code
- Differential fault analysis
