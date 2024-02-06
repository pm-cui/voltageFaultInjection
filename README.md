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
  - GPIO set to have a drive strength os 12mA and high slew. 
  - Prompts user for glitch duration. Calculations to send the register values for delaying the PIO will be added later (take into account rise time)
  - After getting a valid input, runs the State Machine
  
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low
  - Initializes Pin 4 to be the input pin, getting input from PA10 of the STM32
  - Upon a rising edge detected on Pin 4, it induces a voltage glitch on Pin 3
     - Sets the GPIO to LOW for a short amount of time before setting it HIGH 
  - autopull = True causes the OSR to be automatically refilled with the value from the TX FIFO (user input - glitch duration)

- In Pico_Py folder, mosfet_testing.py
   - With the cut-off board, I am able to get a ~200ns glitch timing, goes from 3v3 to 0v and back to 3v3.
   - With the full board, the glitch timing is still ~200ns, but the voltage drops from 3v3 to ~1.5v to 3v3.  

### STM32 Nucleo-F103RB
- Runs an infinite loop, counting from 0 to 3.
- Toggles PA10. 
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32_Disassembly folder. 
- Manipulation of register values is also present in the STM32_Disassembly folder.
- SB12 (remove connection to NRST, which was pulling down the voltage of the MCU), C23, C24, C27, C28, C29 has been removed. Looking to remove c30.
- JP5 and JP6 can be removed.
- CN2's Jumpers can be removed. Doing so allows the use of the ST-Link v2 to program other STM32 boards. 

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
- Driver MOSFET Removed
- Connection of MOSFET is akin to Pull-up/Pull-down resistors.
- Acts as switches to power and ground the STM32

## Current Issues 

### STM32
- Differences between cutoff board and non-cutoff board:
   - C30 removed (AVDD). 
   - R33 removed (Boot 0). Need to connect it to ground to get out of bootloader mode
   - SB2 removed (Connection to JP6. Should not matter to my board as removed JP6's jumper and directly connecting to its pin)
- The cut-off board is able to glitch from 3v3 to 0 to 3v3. The full board does not drop to 0v fast enough

### Fault injection initial tests
- Wires moving during the execution affects the results. It can cause a normal execution to continously reset. Adjusting the wire can sometimes bring it back to normal execution, even with similar glitch timings, and vice versa. 
- Graphs of key fall/rise timings are sketched out
- Osciloscope unable to show the voltage drop when the time/div is 250ms. Need to view in 5ms or lower to see the voltage drop. Likely a limitation of the osciloscope. Voltage glitch appears to drop to 0v

### Bootloader mode
- Unable to initalize USART1
- Looked into chipwhisper's source code to see how they sent the data: https://github.com/newaetech/chipwhisperer/blob/develop/software/chipwhisperer/hardware/naeusb/programmer_stm32fserial.py#L313
   - Replicated the sending of bytes on line 345 of the repo above but not receiving any data
   - Line 313 is the conditionals after receiving the ACK.
   - Line 362 does the XORing of bits
   - Line 412 is the read memory command
   - Tested under an oscilloscope as well. STM32 was receiving data correctly but not transmitting the ACK or NACK as per the flowchart in the documentation

## To Do:
### Raspberry Pi Pico
- Add a function to convert the glitch duration in ns to number of cycles
- Pass the values to PIO to utilize for glitching 
- Nested for loop is available. 4 Registers can be used: OSR, ISR, x, y

### STM32 Nucleo-F103RB
- Using the ST-Link debugger, program the cutoff board and test it

### MOFSET
- No changes to be made as of now.

### Firmware Analysis
- Research on the basics of firmware analysis
- Links used so far:
   -    https://book.hacktricks.xyz/hardware-physical-access/firmware-analysis
   -    https://www.youtube.com/watch?v=zs86OYea8Wk&t=553s
   -    https://www.youtube.com/watch?v=hevWfbWOIew 
   -    https://www.tarlogic.com/blog/owasp-fstm-stage-3-analyzing-firmware/
   -    https://roman1.gitbook.io/blog/embedded-device-exploitation/introduction-to-firmware-analysis
- Practice analyzing firmware of some open source firmware such as: Damn Vulnerable Firmware https://github.com/praetorian-inc/DVRF 

## Future Goals
- Dump the STM32's memory to terminal using VFI.
- As of now:
   - Able to enter bootloader mode
   - Looking into sending data through the USART to use the Bootloader Commands.
- Do firmware analysis on the extracted firmware code
