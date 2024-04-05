; R3 to always store 0x2000_2000 (base address address table)
; R2 to store base address of peripherals & address to jump to send_data_through_UART
; R4 to store data to be written to peripherals
; R0 to store data to be sent through UART

;; Get base address of address table
mov     r2, #0x2000         ; Setting base address 
mov     r3, r2, LSL #16     ; ''
add     r3, r3, r2          ; Base address set to 0x20002000 and stored in r3

;; Write to RCC->CFGR
ldr     r4, [r3, #0x18]     ; Get RCC->CFGR register value
str     r4, [r2, #0x04]     ; Write the value to RCC->CFGR
ldr     r4, [r3, #0x14]     ; Get RCC->CR value
lsls    r4, r4, #6
bpl     line 14

;; Write to RCC->CR
ldr     r2, [r3, #0x10]     ; Get base address of Reset Clock Config (RCC)
ldr     r4, [r3, #0x14]     ; Get RCC->CR value
str     r4, [r2, #0x0]      ; Write the value to RCC->CR

;; Write to Systick->CTRL register
ldr     r2, [r3, #0x1c]     ; Get base address of Systick->CTRL and store it in R2
ldr     r4, [r3, #0x20]     ; Get Systick->CTRL value
str     r4, [r2, #0x0]      ; Write that value to Systick->CTRL


;; Jump to send_data_through_uart
ldr     r2, [r3, #0x08]     ; Get address of send_data_through_UART
movs    r0, #0x42           ; Set data to be transferred
mov     pc, r2              ; mov to send_data_through_UART


Write Mememory:
31 CE
20003000 10
25                          ; 37 + 1 bytes
42F20002
4FEA0243
1344

9C69
5460
5C69
A401
fcd5

1A69
5C69
1460

DA69
1C6A
1460

9A68
4220
9746                        ; 42F200024FEA024313449C6954605C69A401fcd51A695C691460DA691C6A14609A6842209746  (0x0D1812BC, 0xBB)
9e