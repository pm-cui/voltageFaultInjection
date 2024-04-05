mov     r2, #0x2000         ; Setting base address 
mov     r3, r2, LSL #16     ; ''
add     r3, r3, r2          ; Base address set to 0x20002000 and stored in r3
ldr     r2, [r3, #0x0c]     ; Get base address of USART1 and store it in R2
mov     r4, #0x0000240C     ; Set word length to 8 data buts, 1 start bit, n stop bit
str     r4, [r2, #0x0C]     ; Set USART1->CR to the above
ldr     r2, [r3, #0x08]     ; Get address of send_data_through_UART
movs    r0, #0x42           ; Set data to be transferred
mov     pc, r2              ; mov to send_data_through_UART



Write Memory:
31 CE
2000300010
17              ; 23+1 Bytes
42F20002
4FEA0243
1344
DA68
42F20C44
D460
9A68
4220
9746           ; 42F200024FEA02431344DA6842F20C44D4609A6842209746 (4FEA5C47, BE)
A9
