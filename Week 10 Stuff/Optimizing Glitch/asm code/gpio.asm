;cause main program to branch to gpio:
;    mov     r3, #0x08000000         ; ----
;    add     r3, #0x00010000         ; Get the base address of GPIO malicious code
;    mov     pc, r3                  ; Make the PC jump to malicious code

;In hexadecimal (branch section):
;0x4FF00063
;0x03F58033
;0x9F46


turn on GPIO:
    mov     r3, #0x40000000     ; ---
    add     r3, #0x00010800     ; Get base address of GPIO port A register map
    ldr     r2, [r3, #0x0c]     ; Add in the offset to point to GPIO->ODR and load the GPIO ODR register value in r2
    orr     r2, r2, 0x04        ; Set the 3rd bit, corresponding to PA2
    str     r2, [r3, #0x0c]     ; Store the updated value back into the register



In hexadecimal (GPIO section):
0x4FF08043
0x03F58433
0xDA68
0x42F00402
0xDA60
