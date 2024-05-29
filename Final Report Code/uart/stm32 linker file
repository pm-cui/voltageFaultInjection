ENTRY(main)

MEMORY {
	ram_1 (rwx) : ORIGIN = 0x20001000, LENGTH = 4K
	ram_2 (rwx) : ORIGIN = 0x20002000, LENGTH = 4K	
}

SECTIONS {
	.text ORIGIN(ram_1) :
	{
		KEEP(*(.vectors))  /* Vector table */
		*(.text*)          /* Program code */
		*(.rodata*)        /* Read only data */
		. = ALIGN(4);
		_etext = .;
	}

	_sidata = .;

	.data ORIGIN(ram_2) :  AT ( ADDR (.text) + SIZEOF (.text) )
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
