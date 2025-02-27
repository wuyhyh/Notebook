/******************************************************************************
*
 * Name: stackADT.h - 为栈抽象类型定义接口
 * Created on 2025/02/17
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef NOTEBOOK_STACK_H
#define NOTEBOOK_STACK_H

#include <stdbool.h>

typedef int Item;

typedef struct stack_type *Stack;

Stack create(void); // 模块通常不需要create和destroy，但是抽象数据类型需要。
void destroy(Stack s);
void make_empty(Stack s);
bool is_empty(Stack s);
bool is_full(Stack s);
void push(Stack s, Item i);
Item pop(Stack s);

#endif // NOTEBOOK_STACK_H
