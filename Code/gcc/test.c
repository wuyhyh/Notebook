/******************************************************************************
 *
 * Name: test.c - Description
 * Created on 2025/03/12
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PAGE_SIZE 4096
#define MAX_SIZE (PAGE_SIZE * 100)

int main(void)
{
	char *buf = (char *)malloc(MAX_SIZE);
	memset(buf, 0, MAX_SIZE);
	printf("buffer address: 0x%p\n", buf);
	free(buf);

	return 0;
}
