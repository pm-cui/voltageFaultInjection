reset handler registers inits:
    ; Lab_0800658. First bl instruction should not be needed
    mov     r5, #0x08000000         ; Base address to work with
    ldr     r0, [r5, #0x68c]        ; Set up r0 value
    ldr     r1, [r5, #0x690]        ; Set up r1 value
    ldr     r2, [r5, #0x694]        ; Set up r2 value
    movs    r3, 0x0

    ; LAB_08000666
    0x02e0                          ; Branch to the start of the for loop. Check the opcode for branch to understand how it works
    ldr     r4, [r2, r3]            ; Load from flash memory and store into register
    str     r4, [r0, r3]            ; Store value in register into RAM
    adds    r3, #4                  ; Go to the next value in flash

    ; LAB_0800066c
    adds    r4, r0, r3              
    cmp     r4, r1
    0xf9d3                          ; Branch to LAB_08000666 (BCC instruction)
    ldr     r2, [r5, #0x698]    
    ldr     r4, [r5, #0x69c]
    movs    r4, #0x0
    0x01e0                          ; Branch to LAB_0800067e

    ;LAB_0800067a
    str     r3, [r2, #0x0]
    adds    r2, #0x4

    ; LAB_0800067e
    cmp     r2, r4
    0xfbd3                          ; bcc instruction
    add     r6, r5, #0x1000         ; get address of the function
    add     r6, r6, #0x0964         ; get address of the function
    add     lr, pc, #0x4            ; Store the return address in the link register
    mov     pc, r6                  ; Branch to function

    ; hal_init
    mov     r5, #0x08000000         ; Base address
    add     r5, r5, #0x6a4          ; HAL_Init address
    add     lr, pc, #0x04           ; Store the return address in the link register
    mov     pc, r5                  ; Jump to HAL_Init

    ; sys_clk_init
    mov     r5, #0x08000000         ; Base address
    add     r5, r5, #0x1f4          ; sys_clk_init address
    add     lr, pc, #0x04           ; Store the return address in the link register
    mov     pc, r5                  ; Jump to HAL_Init

    ; GPIO-init
    mov     r5, #0x08000000         ; Base address
    add     r5, r5, #0x320          ; sys_clk_init address
    add     lr, pc, #0x04           ; Store the return address in the link register
    mov     pc, r5                  ; Jump to HAL_Init

    ; UART2 init
    mov     r5, #0x08000000         ; Base address
    add     r5, r5, #0x2cc          ; UART2 init
    add     lr, pc, #0x04           ; Store the return address in the link register
    mov     pc, r5                  ; Jump to HAL_Init

    ; UART1 init
    mov     r5, #0x08000000         ; Base address
    add     r5, r5, #0x278          ; UART1 init
    add     lr, pc, #0x04           ; Store the return address in the link register
    mov     pc, r5                  ; Jump to HAL_Init

    ; Assert GPIO
    mov     r3, #0x40000000     ; ---
    add     r3, #0x00010800     ; Get base address of GPIO port A register map
    ldr     r2, [r3, #0x0c]     ; Add in the offset to point to GPIO->ODR and load the GPIO ODR register value in r2
    orr     r2, r2, 0x04        ; Set the 3rd bit, corresponding to PA2
    str     r2, [r3, #0x0c]     ; Store the updated value back into the register


In hexadecimal:
; Register inits
    0x4FF00065
    0xD5F88C06
    0xD5F89016
    0xD5F89426
    0x0023          ; Checksum for this section: 0x9A088870.    String: 4FF00065D5F88C06D5F89016D5F894260023 

    0x02e0
    0xD458
    0xC450
    0x0433          ; Checksum for this section: 0x16DB.        String: 02e0D458C4500433

    0xC418
    0x8C42
    0xf9d3 
    0xD5F89826
    0xD5F89C46
    0x0024
    0x01e0          ; Checksum for this section: 0xB42D.        String: C4188C42f9d3D5F89826D5F89C46002401e0

    0x1360
    0x0432          ; Checksum for this section: 0x1752         String: 13600432

    0xA242
    0xfbd3
    0x05F58056
    0x06F66416
    0xAFF2080E
    0xB746          ; Checksum for this section: 0xACF10299     String: A242fbd305F5805606F66416AFF2080EB746
    
;36F93F4D, fc

    ; Hal init
    0x4FF00065
    0x05F2A465
    0xAFF2080E
    0xAF46          ; Checksum for this section: 0xE5F00348     String: 4FF0006505F2A465AFF2080EAF46

    ;sys_clk_init
    0x4FF00065
    0x05F5FA75
    0xAFF2080E
    0xAF46          ; Checksum for this section: 0xE5F75D58     String: 4FF0006505F5FA75AFF2080EAF46

    ; GPIO Init
    0x4FF00065
    0x05F54875
    0xAFF2080E
    0xAF46          ; Checksum for this section: 0xE5F7EF58     String: 4FF0006505F54875AFF2080EAF46 

    ; UART2 Init
    0x4FF00065
    0x05F53375
    0xAFF2080E
    0xAF46          ; Checksum for this section: 0xE5F79458     String: 4FF0006505F53375AFF2080EAF46 

    ; UART1 Init
    0x4FF00065
    0x05F51E75
    0xAFF2080E
    0xAF46          ; Checksum for this section: 0xE5F7B958     String: 4FF0006505F51E75AFF2080EAF46

    ; Up until here:
    ; Size:         136 bytes
    ; Checksum:     0xD309A305

    ; Assert GPIO
    0x4FF08043
    0x03F58433
    0xDA68
    0x42F00402
    0xDA60          ; Checksum for this section: 0x0EF5007A     String: 4FF0804303F58433DA6842F00402DA60  
;EB059C32, 55
    Size: 152 bytes > 151 is 0x97
    checksum: 0xDDFCA37F > 0xFD
    checksum to be sent: 0x6A
