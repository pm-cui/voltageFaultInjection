ENTRY(main)

MEMORY {
	rom_1 (rwx) : ORIGIN = 0x0801FC00, LENGTH = 4K
	rom_2 (rwx) : ORIGIN = 0x08020C00, LENGTH = 4K	
}

SECTIONS {
	.text ORIGIN(rom_1) :
	{
		KEEP(*(.vectors))  /* Vector table */
		*(.text*)          /* Program code */
		*(.rodata*)        /* Read only data */
		. = ALIGN(4);
		_etext = .;
	}

	_sidata = .;

	.data ORIGIN(rom_2) :  AT ( ADDR (.text) + SIZEOF (.text) )
	{
		_sdata = .;
		*(.data*)      /* Read-write initialized data */
		. = ALIGN(4);
		_edata = .;
	}


	.bss ADDR (.data) + SIZEOF (.data):
	{
		_sbss = .;
		. = ALIGN(4);
		*(.bss*)       /* Read-write zero initialized data */
		*(COMMON)
		. = ALIGN(4);
		_ebss = .;
	}
}

__text_size = SIZEOF (.text);
__data_size = SIZEOF (.data);
__bss_size  = SIZEOF (.bss);
