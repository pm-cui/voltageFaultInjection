/*
 * uart.c
 *
 * Description: UART transmitter example using the PA10 pin for transmission
 *
 * UART setup steps:
 *   1. Enable USARTx clock from RCC
 *   2. Enable Alternate function clock from RCC
 *   3. Enable the relevant GPIO clock from RCC
 *     (Each USART module is connected to a GPIO pair.
 *      You can map them to different pins if supported)
 *   4. Make the GPIO pins alternate-function push-pull output
 *   5. Remap the pins if needed from AFIO->MAPR
 *   6. Enable USART module from CR1
 *   7. Set number of data bits from CR1
 *   8. Set number of stop bits from CR2
 *   9. Set baud rate from BRR
 *   10. Enable transmitter and receiver from CR1
 *   11. Open a terminal and run 'screen /dev/tty.??? 9600'
 *     /dev/tty.??? is the serial port you got on osx / linux when you
 *
 * Author: Furkan Cayci
 *
 *  Project Setup:
 *   EasyMX Pro V7 board
 *   Cortex-M3 arch
 *   STM32F107 chip
 */

/*************************************************
* Definitions
*************************************************/
// This section can go into a header file if wanted
// Define some types for readibility
#define int32_t         int
#define int16_t         short
#define int8_t          char
#define uint32_t        unsigned int
#define uint16_t        unsigned short
#define uint8_t         unsigned char

#define HSE_Value       ((uint32_t) 25000000) /* Value of the External oscillator in Hz */
#define HSI_Value       ((uint32_t)  8000000) /* Value of the Internal oscillator in Hz*/

// Define the base addresses for peripherals
#define PERIPH_BASE     ((uint32_t) 0x40000000)
#define SRAM_BASE       ((uint32_t) 0x20000000)

#define APB1PERIPH_BASE PERIPH_BASE
#define APB2PERIPH_BASE (PERIPH_BASE + 0x10000)
#define AHBPERIPH_BASE  (PERIPH_BASE + 0x20000)

#define AFIO_BASE       (APB2PERIPH_BASE + 0x0000) //   AFIO base address is 0x40010000
#define GPIOA_BASE      (APB2PERIPH_BASE + 0x0800) //  GPIOA base address is 0x40010800
#define USART1_BASE     (APB2PERIPH_BASE + 0x3800) // USART1 base address is 0x40013800

#define RCC_BASE        ( AHBPERIPH_BASE + 0x1000) //   RCC base address is 0x40021000
#define FLASH_BASE      ( AHBPERIPH_BASE + 0x2000) // FLASH base address is 0x40022000

#define NVIC_BASE       ((uint32_t) 0xE000E100)

#define STACKINIT       0x20005000
#define DELAY           7200000

#define AFIO            ((AFIO_type  *)   AFIO_BASE)
#define GPIOA           ((GPIO_type  *)  GPIOA_BASE)
#define RCC             ((RCC_type   *)    RCC_BASE)
#define FLASH           ((FLASH_type *) FLASH_BASE)
#define USART1          ((USART_type *) USART1_BASE)
#define NVIC            ((NVIC_type  *)   NVIC_BASE)

/*
 * Register Addresses
 */
typedef struct
{
	uint32_t CRL;      /* GPIO port configuration register low,      Address offset: 0x00 */
	uint32_t CRH;      /* GPIO port configuration register high,     Address offset: 0x04 */
	uint32_t IDR;      /* GPIO port input data register,             Address offset: 0x08 */
	uint32_t ODR;      /* GPIO port output data register,            Address offset: 0x0C */
	uint32_t BSRR;     /* GPIO port bit set/reset register,          Address offset: 0x10 */
	uint32_t BRR;      /* GPIO port bit reset register,              Address offset: 0x14 */
	uint32_t LCKR;     /* GPIO port configuration lock register,     Address offset: 0x18 */
} GPIO_type;

typedef struct
{
	uint32_t SR;       /* Address offset: 0x00 */
	uint32_t DR;       /* Address offset: 0x04 */
	uint32_t BRR;      /* Address offset: 0x08 */
	uint32_t CR1;      /* Address offset: 0x0C */
	uint32_t CR2;      /* Address offset: 0x10 */
	uint32_t CR3;      /* Address offset: 0x14 */
	uint32_t GTPR;     /* Address offset: 0x18 */
} USART_type;

typedef struct
{
	uint32_t CR;       /* RCC clock control register,                Address offset: 0x00 */
	uint32_t CFGR;     /* RCC clock configuration register,          Address offset: 0x04 */
	uint32_t CIR;      /* RCC clock interrupt register,              Address offset: 0x08 */
	uint32_t APB2RSTR; /* RCC APB2 peripheral reset register,        Address offset: 0x0C */
	uint32_t APB1RSTR; /* RCC APB1 peripheral reset register,        Address offset: 0x10 */
	uint32_t AHBENR;   /* RCC AHB peripheral clock enable register,  Address offset: 0x14 */
	uint32_t APB2ENR;  /* RCC APB2 peripheral clock enable register, Address offset: 0x18 */
	uint32_t APB1ENR;  /* RCC APB1 peripheral clock enable register, Address offset: 0x1C */
	uint32_t BDCR;     /* RCC backup domain control register,        Address offset: 0x20 */
	uint32_t CSR;      /* RCC control/status register,               Address offset: 0x24 */
	uint32_t AHBRSTR;  /* RCC AHB peripheral clock reset register,   Address offset: 0x28 */
	uint32_t CFGR2;    /* RCC clock configuration register 2,        Address offset: 0x2C */
} RCC_type;

typedef struct
{
	uint32_t ACR;
	uint32_t KEYR;
	uint32_t OPTKEYR;
	uint32_t SR;
	uint32_t CR;
	uint32_t AR;
	uint32_t RESERVED;
	uint32_t OBR;
	uint32_t WRPR;
} FLASH_type;

typedef struct
{
	uint32_t EVCR;      /* Address offset: 0x00 */
	uint32_t MAPR;      /* Address offset: 0x04 */
	uint32_t EXTICR1;   /* Address offset: 0x08 */
	uint32_t EXTICR2;   /* Address offset: 0x0C */
	uint32_t EXTICR3;   /* Address offset: 0x10 */
	uint32_t EXTICR4;   /* Address offset: 0x14 */
	uint32_t MAPR2;     /* Address offset: 0x18 */
} AFIO_type;


// Function declarations. Add your functions here
//void copy_data(void);
void set_system_clock_to_8Mhz(void);
int32_t main(void);

/*************************************************
* Vector Table
*************************************************/
// Attribute puts table in beginning of .vector section
//   which is the beginning of .text section in the linker script
// Add other vectors in order here
// Vector table can be found on page 197 in RM0008
uint32_t (* const vector_table[])
__attribute__ ((section(".vectors"))) = {
	(uint32_t *) STACKINIT,         /* 0x000 Stack Pointer                   */
	(uint32_t *) main,              /* 0x004 Reset                           */
};

/*************************************************
* Copy the data contents from LMA to VMA (Load Memory Address | Virtual Memory Address)
*************************************************/
/*
void copy_data(void)
{
	extern char _etext, _sdata, _edata, _sbss, _ebss;
	char *src = &_etext;
	char *dst = &_sdata;

	// ROM has data at end of text; copy it.  
	while (dst < &_edata)
		*dst++ = *src++;

	// Zero bss.  
	for (dst = &_sbss; dst< &_ebss; dst++)
		*dst = 0;
}
*/

void set_system_clock_to_8Mhz(void)
{
	// Enable HSI
	RCC->CR |= 1;
	// Wait untill HSI settles down
	while (!(RCC->CR & (1 << 1)));
	
	// Finally, choose HSI as the system clock
	RCC->CFGR |= (0b00 << 0);

}

/*************************************************
* Main code starts from here
*************************************************/
int32_t main(void)
{
	// Copy LMA to VMA for data section
	//copy_data();

	// Set clock to 8 MHz
	set_system_clock_to_8Mhz();

	/*
	During the De-init sequence, only RCC->CR, RCC->CFGR, Systick CTRL registers were affected
	Other peripherals were not affected, including AFIO, APB, USART configs
	Additionally, RCC->CR and RCC-> CFRG was already set when changing the system clock to utilize HSI clock. Therefore, no need to init it again (we also dont use PLL, saving code space) 
	*/
	
	/*
	// RCC->APB2ENR bit 2 and 14 was already set in the initialization and was not de-init. Maybe only bit 0 needs to be re-init
	// Enable alternate function clock. Bit 0 in RCC APB2ENR register
	RCC->APB2ENR |= (1 << 0);
	// Enable GPIOA clock. Bit 2 in RCC APB2ENR register
	RCC->APB2ENR |= (1 << 2);
	// Enable clock for UART1 clock. Bit 14 in RCC APB2ENR register
	RCC->APB2ENR |= (1 << 14);
	*/
	
	
	
	// Make GPIOA Pin 9,10 (PA9, PA10) alternate-function output (0b1010)
	GPIOA->CRH &= 0xFFFFF00F;
	GPIOA->CRH |= 0x00000BB0;
	

	// Enable USART
	//USART1->CR1 |= (1 << 13);
	// Word length - leave default (8 data)
	//USART1->CR1 |= (0 << 12);
	// Number of stop bits - leave default (1 stop)
	//USART1->CR2 |= (0b00 << 12);
	// Baud rate
	// BRR should be 52 + 1/12 for 9600 baud rate
	// Thus manista is 52 (0x034) and fraction is 12 (0x1) (1/16)
	// Making it 0x0341
	USART1->BRR = 0x0341;
	// Transmitter enable
	//USART1->CR1 |= (1 << 3);
	// Receiver enable
	//USART1->CR1 |= (1 << 2);

	volatile uint32_t *addr = (uint32_t*) 0x08000000; 
	uint32_t value = *addr;
	uint8_t value_8bit;
	
	// for some reason, when nrst is pressed, the first byte does not get transmitted
	// therefore, this is a placeholder to make sure that data does not get lost during testing
	// Might remove this later if needed
	
	value_8bit = (value>>24);
	USART1->DR |= value_8bit;
	while(!(USART1->SR & (1 << 6)));
	
	while(1)
	{
		for(int i=1000000; i>0; i--);
		
		for (int i = 4; i > 0; i--){
			value_8bit = (value >> (8*(i-1)) );
			USART1->DR |= value_8bit;
			while(!(USART1->SR & (1 << 6)));
		}
		
		addr = addr + 1;
		value = *addr;
		
	}

	// Should never reach here
	return 0;
}
