/******************************************************************************
 *
 * Name: rbtree.h - Description
 * Created on 2025/03/12
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef RBTREE_H
#define RBTREE_H

#include <stdio.h>
#include <stdlib.h>

enum color { BLACK, RED };

// 红黑树节点
struct rb_node {
	struct rb_node *rb_parent;
	struct rb_node *rb_right;
	struct rb_node *rb_left;
	int color; // 0: black 1: red
};

struct rb_root {
	struct rb_node *rb_node;
};

// 初始化红黑树
#define RB_ROOT          \
	(struct rb_root) \
	{                \
		NULL     \
	}

#define container_of(ptr, type, member) \
	((type *)((char *)(ptr) - (unsigned long)(&((type *)0)->member)))

#define RB_EMPTY_ROOT(root) ((root)->rb_node == NULL)

void rb_insert(struct rb_node *node, struct rb_root *root);
void rb_erase(struct rb_node *node, struct rb_root *root);
struct rb_node *rb_search(const struct rb_root *root, int key);

void print_rb_tree(struct rb_node *node, int depth);

struct my_rbnode {
	int data;
	struct rb_node node;
};

#endif //RBTREE_H
