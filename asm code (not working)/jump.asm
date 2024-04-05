jump to reset handler:
    mov r3, #0x08000000     ; -----
    add r3, #0x00000658     ; Base address of reset handler
    mov pc, r3              ; Jump to reset handler
    nop
    nop
    nop
    nop



In hexadecimal:
0x4FF00063
0x03F5CB63
0x9F46
0x00BF
0x00BF


Checksum: 5b

10 bytes

String to be sent:
31ce
2000300010
0d
4FF0006303F5CB639F4600BF00BF
56


20002ffc
checksum: f3



4FF0006300bf00bf
db