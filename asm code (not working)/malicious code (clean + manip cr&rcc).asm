; R3 to always store 0x2000_2000 (base address address table)
; R2 to store base address of peripherals & address to jump to send_data_through_UART
; R4 to store data to be written to peripherals
; R0 to store data to be sent through UART

;; Get base address of address table
mov     r2, #0x2000         ; Setting base address 
mov     r3, r2, LSL #16     ; ''
add     r3, r3, r2          ; Base address set to 0x20002000 and stored in r3

;; Write to USART1->CR register
ldr     r2, [r3, #0x0c]     ; Get base address of USART1 and store it in R2
mov     r4, #0x0000240C     ; Set word length to 8 data buts, 1 start bit, n stop bit
str     r4, [r2, #0x0C]     ; Set USART1->CR to the above

;; Write to RCC->CR
ldr     r2, [r3, #0x10]     ; Get base address of Reset Clock Config (RCC)
ldr     r4, [r3, #0x14]     ; Get RCC->CR value
str     r4, [r2, #0x0]      ; Write the value to RCC->CR

;; Write to RCC->CFGR
ldr     r4, [r3, #0x18]     ; Get RCC->CFGR register value
str     r4, [r2, #0x04]     ; Write the value to RCC->CFGR


;; Jump to send_data_through_uart
ldr     r2, [r3, #0x08]     ; Get address of send_data_through_UART
movs    r0, #0x42           ; Set data to be transferred
mov     pc, r2              ; mov to send_data_through_UART



Write Memory:
31 CE
2000300010
21              ; 33+1 Bytes
42F20002
4FEA0243
1344
DA68
42F20C44
D460
1A69
5C69
1460
9C69
5460
9A68
4220
9746            ; 42F200024FEA02431344DA6842F20C44D4601A695C6914609C6954609A6842209746 (4FEAC62E, 4D)
6C