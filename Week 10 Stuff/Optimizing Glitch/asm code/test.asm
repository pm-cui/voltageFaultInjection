initialize UART:


main loop to get memory content:
    mov         r3, #0x08000000 ; Move the base address of flash into r3
    add         r7, sp, #0x0    ; Set r7 to point to the stack top of the stack
    str         r3, [r7, #0]    ; Store the mem address into the stack. Not redundant as we need to increment the value later
    ldr         r3, [r7, #0]    ; Load the variable from stack into r3
    sub         sp, #0x04       ; Move the stack pointer to top of stack
    add         r7, sp, #0x0    ; Move r7 to point to stack pointer
    ldr         r3, [r3, #0]    ; Load memory content into r3
    str         r3, [r7, #0x0]  ; Store the memory contents to the stack

send data via uart (in bootloader mode):    ;
    mov         r1, #0x40000000         ; Set r1 to the address of USART1 peripheral
    add         r1, r1, #0x00018000     ; r1 will contain the address to USART1 now
    str         r3, [r1, #0x04]         ; Store the value r3 into USART1 Data Register
    mov         r2, pc                  ; Get address of the next instruction and store it into r2. PC contains address of next instruction in thumb mode
    
    ;wait for TC(transmit complete) to be cleared. If need be, add some nop instructions
    ldrh        r0, [r1, #0]            ; Load USART status registers to r0
    lsls        r0, r0, #0x19           ; Logical shift such that TC is the MSB
    strbpl      pc, [r2]                ; Branch back to ldrh instruction if TC is not yet complete
