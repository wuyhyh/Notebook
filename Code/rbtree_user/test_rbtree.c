/******************************************************************************
 *
 * Name: test_rbtree.c - Description
 * Created on 2025/03/12
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "rbtree.h"
#include <stdio.h>
#include <stdlib.h>

/*
int main(void)
{
	struct rb_root my_tree = RB_ROOT;

	//  插入10000个随机数
	for (int i = 0; i < 10000; i++) {
		struct my_rbnode *new_node = malloc(sizeof(struct my_rbnode));
		new_node->data = rand() % 10000;
		rb_insert(&new_node->node, &my_tree);
	}
	struct my_rbnode *temp_node = malloc(sizeof(struct my_rbnode));
	temp_node->data = 100;
	rb_insert(&temp_node->node, &my_tree);

	printf("Printing Red-Black Tree:\n");
	print_rb_tree(my_tree.rb_node, 0);

	// 查找
	int key = 100;
	struct rb_node *result = rb_search(&my_tree, key);
	if (result) {
		struct my_rbnode *found =
			container_of(result, struct my_rbnode, node);
		printf("Found key = %d\n", found->data);
	} else {
		printf("Not found\n");
	}

	return 0;
}
*/

int main()
{
	struct rb_root my_tree = RB_ROOT;
	//  测试删除
	int values[] = { 20, 15, 25, 10, 18, 22, 30, 5, 12, 17 };
	struct my_rbnode *nodes[10];

	for (int i = 0; i < 10; i++) {
		nodes[i] = malloc(sizeof(struct my_rbnode));
		nodes[i]->data = values[i];
		rb_insert(&nodes[i]->node, &my_tree);
	}

	printf("Printing Red-Black Tree:\n");
	print_rb_tree(my_tree.rb_node, 0);

	// 查找并删除 15
	struct rb_node *result1 = rb_search(&my_tree, 15);
	if (result1) {
		struct my_rbnode *found =
			container_of(result1, struct my_rbnode, node);
		printf("Found: %d, deleting...\n", found->data);
		rb_erase(&found->node, &my_tree);
		free(found);
	}

	printf("Printing Red-Black Tree:\n");
	print_rb_tree(my_tree.rb_node, 0);

	// 再次查找 15，应该找不到
	result1 = rb_search(&my_tree, 15);
	if (!result1) {
		printf("15 successfully deleted!\n");
	}

	return 0;
}
