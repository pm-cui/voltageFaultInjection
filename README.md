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
- Make a terminal UI to allow users to input the frequency to run the PIO at and the duration of the glitch.
   

## Progress
### Raspberry Pi Pico (using micropython and asm_PIO)
- Main Program
  - State Machine running at a set 100Mhz
  - Prompts user for glitch duration. Calculations to send to PIO will be added later
  - After getting a valid input, runs the State Machine
  
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low
  - Initializes Pin 4 to be the input pin, getting input from PA10 of the STM32
  - Upon a rising edge detected on Pin 4, it induces a voltage glitch on Pin 3
  - autopull = True causes the OSR to be automatically refilled with the value from the TX FIFO (user input - glitch duration)

### STM32 Nucleo-F103RB
- Runs an infinite loop, counting from 0 to 3.
- Toggles PA10. 
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32_Disassembly folder. 
- Manipulation of register values is also present in the STM32_Disassembly folder.
- JP5 can be removed
- SB12(remove connection to NRST, which was pulling down the voltage of the MCU), C23, C24, C27, C28, C29 has been removed

### STM32 Nucleo-F103RB (with ST-Link component cut off)
- Conection to ST-Link are as follows:
   - Boot 0 (CN7 Pin 7) to GRD
   - 3v3 to Pico's 3v3
   - VIN to ST-Link CN4 Pin 1
   - CN7 Pin 15 to ST-Link CN4 Pin 2
   - GND to ST-Link CN4 Pin 3
   - CN7 Pin 13 to ST-Link CN4 Pin 4
   - NRST to ST-Link CN Pin 5
- ST-Link able to recognise the board but unable to read/erase/write the board
- Screenshots documenting this issue is in CutOff_STM32_Issue

### P&N MOSFET
- Connection of MOSFET is akin to Pull-up/Pull-down resistors.
- Acts as switches to power and ground the STM32
 
### Driver MOSFET
- Acts as a Pull-up Resistor.
- When Pin 3's output is 0, Driver MOSFET's Gate is open and voltage is supplied to PG1 and NG1. P-Channel MOSFET is opened and no voltage is supplied to STM.
- When Pin 3's output is 1, Driver MOSFET's Gate is closed and causes the circuit to short to GRD, causing PG1 and NG1 to not be powered. P-channel MOSFET is closed and N-Channel MOSFET is opened and voltage is supplied to STM.

## Current Issues
- Rise and Fall Time are still too long, even with the driver MOSFET Setup
- When conducting the fault injection with the current setup, voltage drop is inconsisten. THe dropped voltage ranges from apprioximately 2v to 1v
- During the execution, tx of STM32 will sometimes stop transmitting data. Resetting it will continue its operationoving
- Wires moving during the execution affects the results. It can cause a normal execution to continously force reset. Adjusting the wire can sometimes bring it back to normal execution.
- ST-Link v2 is unable to read/erase the memory of the cutoff stm32 board
- Will test with the cut-off board and compare results to determine what the issue is
- Circuit design verified to be correct
- Find out the potential issues
- Differences between cutoff board and my board:
   - C30 removed (AVDD). 
   - R33 removed (Boot 0). Need to connect it to ground to get out of bootloader mode
   - SB2 removed (Connection to JP6. Should not matter to my board as removed JP6's jumper and directly connecting to its pin)   

## Results of Current Setup
- Note: In the paper Shaping the Glitch, their drop was only took ~50ns. The total glitch time was approximately 200ns.
  
### No driver MOSFET, not connected to STM
- Rise time: ~100ns, Fall time: ~100ns

### Driver MOSFET ONLY , Not connected to PG1 and NG1, using 220 Ohms resistor
- Rise time: ~50ns, Fall time: ~20ns (capacitors present)
- Rise time: ~75ns, Fall time: ~20ns (capacitors removed)

### Driver MOSFET, Not connected to PG1 and NG1, using 10k Ohms resistor
- Rise and Fall Time increases signinficantly

### Driver MOSFET, Connected to PG1 and NG1, using 220 Ohms resistor
- Rise time: ~200ns, Fall time: ~500ns           (capacitors present)
- Rise time: ~1 microsecond, Fall time: ~100ns   (capacitors removed)

### Driver MOSFET, Connected to PG1 and NG1, using 220 Ohms resistor, Connected to STM32
- Rise time: ~7.5 microseconds, Fall time: ~10 microseconds (capacitors present)
- Rise time: ~2 microseconds, Fall time: ~2.5 microseconds (capacitors removed)



## To Do:
### Raspberry Pi Pico
- Add a function to convert the glitch duration in ns to number of cycles
- Pass the values to PIO to utilize for glitching
- Nested for loop is available. 4 Registers can be used: OSR, ISR, x, y


### STM32 Nucleo-F103RB
- Using the ST-Link debugger, program the cutoff board and test it

### MOFSET
- No changes to be made as of now.

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
