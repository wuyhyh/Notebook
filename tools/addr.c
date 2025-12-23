/******************************************************************************
 *
 * Name: addr.c - Description
 * Created on 2025/10/14
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>

int bss_var = 1;
int data_var = 1;

int main(int argc, char *argv[])
{
	void *stack_var;
	stack_var = (void *)main;
	printf("Hello World! main is executing at %p\n", stack_var);
	printf("This address (%p) is in our stack frame!\n", &stack_var);
	printf("This address (%p) is in our bss section\n", &bss_var);
	printf("This address (%p) is in our data section\n", &data_var);

	return 0;
}
