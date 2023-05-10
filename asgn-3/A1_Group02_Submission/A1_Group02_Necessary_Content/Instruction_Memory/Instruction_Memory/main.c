#define F_CPU 1000000UL
#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h> 

volatile uint16_t INSTRUCTIONS[1<<8] = {
	0x706f,0x7013,0x102e,0x2127,0xa123,0xe724,0x3213,0xb221,0xc321,0x91c0,0xd331,0x6224,0x3610,0x1661,0x3620,0x1661,0x91a0,0x4727,0x8421,0x0115,0x7661,0x6620,0x5241,0x7661,0x6610,0x91c0,0xc271,0x9110,
};

//ISR(INT0_vect){
	//uint16_t instruction;
	//instruction = INSTRUCTIONS[PINA];
	//PORTC = (uint8_t) instruction;
	//PORTB = (uint8_t) (instruction >> 8);
	//_delay_ms(50);
//}

int main(void)
{
	// Some pins of PORTC can not be used for I/O directly.
	// turn of JTAG to use them
	// o write a 1 to the JTD bit twice consecutively to turn it off
	MCUCSR = (1<<JTD);  MCUCSR = (1<<JTD);
	
	DDRA = 0x00;	// input pc
	
	// Instruction : D[7:0]C[7:0]
	DDRC = 0xFF;	// lower 8-bits of instruction
	DDRB = 0xFF;	// upper 8-bits of instruction
	
	uint8_t pc = -1;
	uint16_t instruction;
	/* Replace with your application code */
	while (1)
	{
		if (PINA != pc) {
			pc = PINA;
			instruction = INSTRUCTIONS[pc];
			PORTC = (uint8_t) instruction;
			PORTB = (uint8_t) (instruction >> 8);
			_delay_ms(50);
		}
	}
}

