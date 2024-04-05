mov     r2, #0x2000         ; Setting base address 
mov     r3, r2, LSL #16     ; ''
add     r3, r3, r2          ; Base address set to 0x20002000
ldr     r2, [r3, #0x08]     ; Get address of send_data_through_UART
movs    r0, #0x42           ; Set data to be transferred
mov     pc, r2              ; mov to send_data_through_UART


Write Memory:
31 CE
20003000 10
0f              ; 15+1 Bytes
42F20002
4FEA0243
1344
9A68
4220
9746            ; 42F200024FEA024313449A6842209746 (0x0D185E0B, 40)
4F