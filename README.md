# Voltage Fault Injection
- Develop a fault injector hardware prototype using a low-cost development board (Raspberry Pi Pico)
- Execute fault injection using the developed fault injector against different products
- Study why some products are more susceptible to fault injections by extracting the MCU ROM code to identify possible failure points.

## Progress
### Raspberry Pi Pico (using micropython and asm_PIO)
- Main Program
  - Prompt user to input the frequency of the State Machine (once at the start of the program)
  - After getting a valid input, runs the State Machine. (refer to PIO)
  - Prompts user to input the duration of the glitch (Repeated)
  
- asm_PIO
  - Initializes Pin 3 to be the output pin, with default state being low.
  - autopull = False -> Does not automatically refill the OSR with the value from the TX FIFO. This causes the PIO to wait for user input before causing the glitch.
  - Waits for user input from the main program to be written to the TX FIFO before causing the glitch.

### STM32 Nucleo-F103RB
- Runs an infinite loop, counting from 0 to 3.
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32Disassembly.png
- Outputs via USB to laptop's terminal

## To Do
### Raspberry Pi Pico
- Glitch timing from user input is not yet accurate as of now. Will work on it after getting a glitch correctly. For now, I have to manually change the timing of the glitch.

### STM32 Nucleo-F103RB
- Study the schematics and figure out the connections to the MOSFET for dropping the voltage.

## Future Goals
- Dump the STM32's memory to terminal using VFI.
- Currently after looking at the documentation for the STM32 (needs to verify if its correct):
  - Boot0 Pin should be set to 1, Boot1 Pin should be set to 0. This pattern will enable bootloader mode. (found in pg 75 of AN2606)
  - Press the reset button on the STM32 board
  - Send 0x7F on any one of the 3 USART pins to configure that USARTx Pins. 
  - In bootloader mode, the STM32 takes in various commands through the USARTx Pins, notably the Read Memory Command. (found in pg 15 of AN3155)
  - Following the flowchart present on pg 16, a glitch should be sent after the byte-string is sent to STM to skip the Read Protection and cause it to dump specified blocks of memory. 
