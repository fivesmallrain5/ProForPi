#include "unittest.h"
#include "stdio.h"

void uart1SendChars(u8 *str, u8 strlen)
{
	u8 i = 0;
	printf("\n´®¿ÚÊä³ö£º");
	for (i = 0; i < strlen; i++)
	{
		printf("%x ", str[i]);
	}
	printf("\n");
}