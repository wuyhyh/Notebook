/******************************************************************************
 *
 * Name: test_list.c - Description
 * Created on 2025/03/12
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "list.h"
#include <stdio.h>
#include <stdlib.h>

struct my_node {
	int data;
	struct list_head list;
};

int main(void)
{
	LIST_HEAD(my_list); // 定义链表头
	struct my_node *entry;

	// 添加100个节点
	for (int i = 0; i < 100; i++) {
		struct my_node *node =
			(struct my_node *)malloc(sizeof(struct my_node));
		if (!node) {
			perror("malloc failed");
			exit(EXIT_FAILURE);
		}
		node->data = i;
		list_add_tail(&node->list, &my_list);
		printf("added data %d at address %p\n", i, node);
	}

	// 遍历链表并输出
	list_for_each_entry(entry, &my_list, list) {
		printf("Data: %d at address %p, next: %p, prev: %p\n",
		       entry->data, entry, entry->list.next, entry->list.prev);
	}

	// 释放链表节点
	struct list_head *pos, *n;
	list_for_each_safe(pos, n, &my_list) {
		entry = container_of(pos, struct my_node, list);
		free(entry);
	}

	return 0;
}
