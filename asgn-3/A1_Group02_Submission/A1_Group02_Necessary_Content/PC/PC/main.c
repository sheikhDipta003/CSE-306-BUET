#define F_CPU 1000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

volatile uint8_t curr = 0;

ISR(INT1_vect)
{
	PORTB = curr;
	_delay_ms(500);
	curr = PINA;
	//GIFR = (1 << INTF0);
	//GIFR = (1 << INTF1);
}
ISR(INT0_vect)//STEP2
{
	curr = 0;
	PORTB = 0;
}
int main(void)
{
	DDRA = 0x00;
	DDRB = 0xFF;
	
	GICR = (1 << INT1);
	GICR |= (1 << INT0);
	MCUCR = MCUCR | (1 << ISC11);
	MCUCR = MCUCR & (~(1 << ISC10));
	MCUCR = MCUCR | (1 << ISC01);
	MCUCR = MCUCR & (~(1 << ISC00));
	sei();
	while(1);
}


