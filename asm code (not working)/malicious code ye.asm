mov     r2, #0x2000         ; Setting base address 
mov     r3, r2, LSL #16     ; ''
add     r3, r3, r2          ; Base address set to 0x20002000
movs    r0, #0x42           ; Set data to be transferred
ldr     r1, [r3, #0x0C]      ; Get USART1 base address
str     r0, [r3, #0x04]
ldr     r0, [r1, #0x00]
lsl     r0, r0, #0x19
bpl
bx      ldr


Write Mem:
31 CE
20003000 10
19          ; 25+1 bytes
42F20002
4FEA0243
1344
4220
D968
5860
0868
4FEA4060
fbd5
7047        ; 42F200024FEA024313444220D968586008684FEA4060fbd57047 (0x42F211B7, 16)
0F

https://github.com/fcayci/stm32f1-bare-metal/blob/master/uart/stm32.ld