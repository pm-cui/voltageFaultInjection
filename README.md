# Voltage Fault Injection
- Develop a fault injector hardware prototype using a low-cost development board (Raspberry Pi Pico)
- Execute fault injection using the developed fault injector against different products
- Study why some products are more susceptible to fault injections by extracting the MCU ROM code to identify possible failure points.

## Nagivation
- main.c --> STM32's main program code
- STM32 Disassmebly Folder --> Screenshots of STM32's Disassembly window and register manipulation
- voltage.py --> Main code for pico. Contains the main program and PIO code
- Pico_Py folder --> Test codes for the various building blocks

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
  
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low
  - Initializes Pin 4 to be the input pin, getting input from PA10 of the STM32
  - Gets 2 inputs from the main program: Glitch & Delay duration:
     - Moves Glitch duration to ISR
     - Delay Duration to stay in OSR
     - The pulling of values only occurs once
  - Upon a rising edge detected on Pin 4:
     - Delays for the number of clock cycles stated in the ISR
     - Sets Pin 3 High for the number of clock cycles stated in OSR
     - Sets Pin 3 Low for a small period of time before waiting for a falling edge. (prevents continous glitching)
  - autopull = True causes the OSR to be automatically refilled with the value from the TX FIFO (user input - glitch duration)

- In Pico_Py folder, mosfet_testing.py
   - With the cut-off board, I am able to get a ~200ns glitch timing, goes from 3v3 to 0v and back to 3v3.
   - With the full board, the glitch timing is still ~200ns, but the voltage drops from 3v3 to ~1v to 3v3.
 
- voltage_testing.py
   - Slight change to voltage.py:
      - Automates the process of changing the delay and glitch durations
      - Outputs any abnormal data to an output file

### STM32 Nucleo-F103RB
- Runs an infinite loop, counting from 1 to 4, with i and j representing 0 to 3 in binary. 
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

### Button
- Added a button to the circuit
- A button press causes a rising edge and is used to manually trigger the rising edge
- Only STM32 OR button should be connected to Pin 4 of Pico at any one period of time

### Ghidra
- STM32 is a Bare Metal system, application runs directly on the hardware
- Memory-mapped peripherals, Check datasheet of the processor for memory map ***
- Followed along with the video and used Ghidra to analyze the given firmware files

## Current Issues 

### Pico (pio_asm)
- Currently, only one register is available for glitch timing and delay duration respectively
- This limits how long the glitch can be, up to 32 nop(). Trade off btw accuracy and length if multiple nop() are use
- Although scratch registers are 32 bits, only 5 bits are DATA bits. (3.4.10.2 Operation)
- set() would clear all bits but the 5 LSB (data bits). All other operations will retain the full 32 bits.
- PIO instructions only works with values ranging from 0-31. Anything higer and the program exhibits abnormal behaviour
- My implementation/idea was to utilize 1 register to hold the number of cycles which delay duration was going to delay for
   - bits 0-4 and bits 5-9 would hold the number of cycles to delay for
   - nop()  [31] -> Loop this [bit 0-4] number of times
   - nop() -> Loop this [bit 5-9] number of times
   - However, this implementation is currently not possible
- PULL instruction REMOVES a 32bit word from the TX FIFO before placing it on the OSR (NOT copies)
   - Unable to refresh the delay duration's value from main program (ASM and Main prog run at diff speeds, asm runs much faster than python)
   - OUT instruction does not work as TX FIFO is cleared (along with autopull)
   - Shift registers are useful but we only have access to 2 of them (OSR, ISR)
- 2 registers are already used for glitch duration. At least 3 registers are needed OR being able to access specific bits in a scratch registers are required in order to increase the acceptable range of delay duration
   - A nested for loop would decrement 2 register values
   - One more needed to store the original value 

### STM32
- Differences between cutoff board and non-cutoff board:
   - C30 removed (AVDD). 
   - R33 removed (Boot 0). Need to connect it to ground to get out of bootloader mode
   - SB2 removed (Connection to JP6. Should not matter to my board as removed JP6's jumper and directly connecting to its pin)
- The cut-off board is able to glitch from 3v3 to 0 to 3v3. The full board does not drop to 0v even with incresing the glitch timings

### Oscilloscope 
- Unable to show voltage drop when time/div is 250ms. Need to view in 5ms or lower
- Likely to be limitation of oscilloscope, although at 5ms/div, voltage glitch appears but it is inconsistent in its drop.
- The osciloscope does not show a stable graph at 5ms/div. Might need help for oscilloscope settings

### Hardware Issues
- Wires moving during the execution affects the results. It can cause a normal execution to continously reset. Adjusting the wire can sometimes bring it back to normal execution, even with similar glitch timings, and vice versa. 
- Graphs of key fall/rise timings are sketched out

### Testing (Rising edge)
- Results of the initial tests using voltage_testing.py is shown in the "Test_Results(Fail).png"
- Test is as follows:
   - Find the glitch duration which always forces the STM32 to reset
   - Look at the disassembly of STM32 to identify possible weak points to glitch
   - Using a nested for loop, brute force the glitch & delay timings
   - Each loop runs for 1min 30 sec. Entering the loop will output the glitch and delay cycles to an output file (one time).
   - Program will write any abnormal output to the output file as well, indicating which glitch/delay cycle the glitch occured
- No successful runs were found

### Testing (Button input)
- Connected a button to the circuit
- When pressed, a rising edge will be detected by Pin 4, triggering the glitch
- Varied the glitch duration while testing
- No successful runs were found

### Force resetting of STM
- Tried 2 methods: Using MOSFET to short the 3v3 to ground | Reset the pico using machine.reset()
- MOSFET does not fully short to ground
- machine.reset() causes the pico to disconnect from Thonny IDE and sotp execution

### Fritzing (circuit design software)
- Only paid version available

### Bootloader mode
- Unable to initalize USART1
- Looked into chipwhisper's source code to see how they sent the data: https://github.com/newaetech/chipwhisperer/blob/develop/software/chipwhisperer/hardware/naeusb/programmer_stm32fserial.py#L313
   - Replicated the sending of bytes on line 345 of the repo above but not receiving any data
   - Line 313 is the conditionals after receiving the ACK.
   - Line 362 does the XORing of bits
   - Line 412 is the read memory command
   - Tested under an oscilloscope as well. STM32 was receiving data correctly but not transmitting the ACK or NACK as per the flowchart in the documentation
- Unable to find any examples online that utilizes bootloader commands
  
## To Do:
### Raspberry Pi Pico
- N changes as of now. 

### STM32 Nucleo-F103RB
- Desolder c30 from the full board. 

### MOFSET
- No changes as of now.

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
- As of now:
   - Able to enter bootloader mode
   - Looking into sending data through the USART to use the Bootloader Commands.
- Do firmware analysis on the extracted firmware code
