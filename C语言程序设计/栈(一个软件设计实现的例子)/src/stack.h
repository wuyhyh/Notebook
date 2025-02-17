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

void make_empty(void);
bool is_empty(void);
bool is_full(void);
void push(int i);
int pop(void);

#endif // NOTEBOOK_STACK_H
