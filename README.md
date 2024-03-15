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
- Glitching was successful in glitching into user code running into STM32 program
- Now attempting to glitch the STM32 bootloader mode, specifically, the Read Memory Command to extract the Bootloader Code
   
## Progress
### Raspberry Pi Pico (using micropython and asm_PIO)
- Main Program 
  - State Machine running at a set 100Mhz
  - Loops over a range of glitch and delay durations, with a step of 20ns
  - Any unexpected results will be appended to a file on chip
  - voltage_testing.py is made for glitching user code
  - VFI_on_STM.py is made for glitching bootloader mode
     - Specific commands to send to STM are found in STM32's documentation (AN3155)
 
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low
  - Initializes Pin 4 to be the input pin, getting input from PA10 of the STM32
  - Gets Glitch and Delay durations using the ISR to shift bits out.
  - Connect Pin 4 to Pin 12(TX). Waits for a specific number of rising edge before asserting the glitch. 

### STM32 Nucleo-F103RB
- To enter bootloader mode and interface with Pico:
   - PB2(boot1) connected to ground
   - Boot0 connected to 3v3 of Pico
   - 3v3 of STM connected to MOSFET's output
- RDP is set
- CN4 Pin connection:
   - 1) VDD
     2) PA14
     3) Grd
     4) PA13
     5) NRST
   - Connected 3v3 to VDD too
      

## Current Issues 
- Glitching user's code is successful
- However, glitching bootloader mode always returns a "-1" output and does not bypass the RDP check.
  

## Future Goals
- Dump the STM32's memory to terminal using VFI.
- Do firmware analysis on the extracted firmware code
- Look into breaking common encryption methods such as RSA, with differential fault attacks
