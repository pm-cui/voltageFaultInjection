jump to reset handler:
    mov r3, #0x08000000     ; -----
    add r3, #0x00000658     ; Base address of reset handler
    mov pc, r3              ; Jump to reset handler



In hexadecimal:
0x4FF00063
0x03F5CB63
0x9F46