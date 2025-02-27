/******************************************************************************
*
 * Name: stack_client.c - 测试栈抽象数据类型
 * Created on 2025/02/17
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "stackADT.h"
#include <stdio.h>

int main(void)
{
	Stack s1, s2;
	int n;

	s1 = create();
	s2 = create();

	push(s1, 1);
	push(s1, 2);

	n = pop(s1);
	printf("Popped %d from s1\n", n);
	push(s2, n);
	n = pop(s1);
	printf("Popped %d from s1\n", n);
	push(s2, n);

	destroy(s1);

	while (!is_empty(s2)) {
		printf("Popped %d from s2\n", pop(s2));
	}

	push(s2, 3);
	make_empty(s2);
	if (is_empty(s2))
		printf("s2 is empty.\n");
	else
		printf("s2 is not empty.\n");

	destroy(s2);

	return 0;
}
