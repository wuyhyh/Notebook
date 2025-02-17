/******************************************************************************
 *
 * Name: stack2.c - 使用链表实现栈
 * Created on 2025/02/17
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "stack.h"
#include <stdio.h>
#include <stdlib.h>

struct node {
	int data;
	struct node *next;
};

static struct node *top = NULL;

static void terminate(const char *message)
{
	printf("%s\n", message);
	exit(EXIT_FAILURE);
}

void make_empty(void)
{
	while (!is_empty()) {
		pop();
	}
}

bool is_empty(void)
{
	return top == NULL;
}

bool is_full(void)
{
	return false; // 链表实现不会满
}

void push(int i)
{
	struct node *new_node = malloc(sizeof(struct node));
	if (new_node == NULL) {
		terminate("Error in push: stack is full.");
	}

	new_node->data = i;
	new_node->next = top;
	top = new_node;
}

int pop(void)
{
	struct node *old_top;
	int i;

	if (is_empty()) {
		terminate("Error in pop: stack is empty.");
	}

	old_top = top;
	i = top->data;
	top = top->next;
	free(old_top);
	return i;
}
