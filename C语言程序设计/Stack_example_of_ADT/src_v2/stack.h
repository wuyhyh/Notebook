/******************************************************************************
 *
 * Name: stack.h - Description
 * Created on 2025/02/17
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef NOTEBOOK_STACK_H
#define NOTEBOOK_STACK_H

#include <stdbool.h>

#define STACK_SIZE 100

typedef struct {
	int contents(STACK_SIZE);
	int top;
} Stack;

void make_empty(Stack *s);
bool is_empty(Stack *s);
bool is_full(Stack *s);
void push(Stack *s, int i);
int pop(Stack *s);

#endif // NOTEBOOK_STACK_H
