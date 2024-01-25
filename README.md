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
  - Causes GPIO to be asserted for a short amount of time before turning returning to a low state

### STM32 Nucleo-F103RB
- Runs an infinite loop, counting from 0 to 3.
- Contains a if statement that can never be reached. This is not optimized out as seen from the STM32_Disassembly.png
- Outputs via USB to laptop's terminal

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
- With JP6 attached, STM32 is able to transmit data over to laptop via USB. However, it also connects the capacitors, leading to a slower drop in voltage to ground
- With JP6 detached, STM32 is no longer able to transmit data over to laptop via USB. However, the drop in voltage is steeper and faster.
- In both cases, there is a slow curve before hitting 0v. Look into capacitors schematics.
- Perhaps transmit data from STM32 to Pico over the UART Pins.
- Look to where are the capacitors and how to remove/ground them without affecting the usb transmit of data. 

## To Do:
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
