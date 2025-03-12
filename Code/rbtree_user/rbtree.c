/******************************************************************************
 *
 * Name: rbtree.c - Description
 * Created on 2025/03/12
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "rbtree.h"

// 左旋
static void rb_rotate_left(struct rb_node *node, struct rb_root *root)
{
	if (!node || !node->rb_right) {
		fprintf(stderr,
			"Error: attempt to left-rotate a node without right child!\n");
		return;
	}

	struct rb_node *right = node->rb_right; // 右子节点
	node->rb_right = right->rb_left; // 右子节点的左子树移到当前节点的右子树

	// 只有当 `right->rb_left` 不是 NULL 时，才更新 `rb_parent`
	if (right->rb_left) {
		right->rb_left->rb_parent = node;
	}

	// 更新 `right` 的父节点
	right->rb_parent = node->rb_parent;
	if (!node->rb_parent) {
		root->rb_node =
			right; // 如果 `node` 是根节点，则 `right` 成为新的根
	} else if (node == node->rb_parent->rb_left) {
		node->rb_parent->rb_left = right;
	} else {
		node->rb_parent->rb_right = right;
	}

	// `right` 现在成为 `node` 的父节点
	right->rb_left = node;
	node->rb_parent = right;
}

// 右旋
static void rb_rotate_right(struct rb_node *node, struct rb_root *root)
{
	struct rb_node *left = node->rb_left;

	// 左子节点的右子树移动到当前节点的左子树
	node->rb_left = left->rb_right;
	if (left->rb_right)
		left->rb_right->rb_parent = node;

	// 更新父节点指向
	left->rb_parent = node->rb_parent;
	if (!node->rb_parent)
		root->rb_node = left;
	else if (node == node->rb_parent->rb_right)
		node->rb_parent->rb_right = left;
	else
		node->rb_parent->rb_left = left;

	// 旋转
	left->rb_right = node;
	node->rb_parent = left;
}

// 插入修正
static void rb_insert_fixup(struct rb_node *node, struct rb_root *root)
{
	struct rb_node *parent;
	struct rb_node *grand_parent;

	while ((parent = node->rb_parent) && parent->color == RED) {
		grand_parent = parent->rb_parent;

		if (parent == grand_parent->rb_left) {
			struct rb_node *uncle = grand_parent->rb_right;

			if (uncle &&
			    uncle->color == RED) { // 叔节点是红色，颜色翻转
				uncle->color = BLACK;
				parent->color = BLACK;
				grand_parent->color = RED;
				node = grand_parent;
				continue;
			}

			if (node == parent->rb_right) { // 先左旋
				rb_rotate_left(parent, root);
				struct rb_node *tmp = parent;
				parent = node;
				node = tmp;
			}

			// 右旋并调整颜色
			parent->color = BLACK;
			grand_parent->color = RED;
			rb_rotate_right(grand_parent, root);
		} else {
			struct rb_node *uncle = grand_parent->rb_left;

			if (uncle &&
			    uncle->color == RED) { // 叔节点是红色，颜色翻转
				uncle->color = BLACK;
				parent->color = BLACK;
				grand_parent->color = RED;
				node = grand_parent;
				continue;
			}

			if (node == parent->rb_left) { // 先右旋
				rb_rotate_right(parent, root);
				struct rb_node *tmp = parent;
				parent = node;
				node = tmp;
			}

			// 左旋并调整颜色
			parent->color = BLACK;
			grand_parent->color = RED;
			rb_rotate_left(grand_parent, root);
		}
	}

	// 保证根节点始终是黑色
	root->rb_node->color = BLACK;
}

// 插入节点
void rb_insert(struct rb_node *node, struct rb_root *root)
{
	struct my_rbnode *entry = container_of(node, struct my_rbnode, node);
	printf("Inserting key: %d\n", entry->data);

	struct rb_node **link = &root->rb_node;
	struct rb_node *parent = NULL;

	while (*link) {
		parent = *link;
		if ((long)node < (long)*link)
			link = &(*link)->rb_left;
		else
			link = &(*link)->rb_right;
	}

	// 连接新节点
	node->rb_parent = parent;
	node->rb_left = node->rb_right = NULL;
	node->color = RED;

	if (parent) {
		if ((long)node < (long)parent)
			parent->rb_left = node;
		else
			parent->rb_right = node;

	} else
		root->rb_node = node;

	rb_insert_fixup(node, root);
}

// 替换子树
static void rb_transplant(struct rb_root *root, struct rb_node *old,
			  struct rb_node *new)
{
	if (!old->rb_parent)
		root->rb_node = new; // 如果 old 是根节点，直接替换
	else if (old == old->rb_parent->rb_left)
		old->rb_parent->rb_left = new; // old 是左子节点
	else
		old->rb_parent->rb_right = new; // old 是右子节点
	if (new)
		new->rb_parent = old->rb_parent; // 更新父节点指向
}

// 删除修正
static void rb_erase_fixup(struct rb_root *root, struct rb_node *node)
{
	while (node != root->rb_node && (!node || node->color == BLACK)) {
		struct rb_node *sibling;
		if (node == node->rb_parent->rb_left) { // node 是左子节点
			sibling = node->rb_parent->rb_right;

			if (sibling &&
			    sibling->color == RED) { // Case 1: 兄弟节点是红色
				sibling->color = BLACK;
				node->rb_parent->color = RED;
				rb_rotate_left(node->rb_parent, root);
				sibling = node->rb_parent->rb_right;
			}

			if ((!sibling->rb_left ||
			     sibling->rb_left->color == BLACK) &&
			    (!sibling->rb_right ||
			     sibling->rb_right->color ==
				     BLACK)) { // Case 2: 兄弟节点的子节点全是黑色
				sibling->color = RED;
				node = node->rb_parent;
			} else {
				if (!sibling->rb_right ||
				    sibling->rb_right->color ==
					    BLACK) { // Case 3: 兄弟的左子是红色，右子是黑色
					sibling->rb_left->color = BLACK;
					sibling->color = RED;
					rb_rotate_right(sibling, root);
					sibling = node->rb_parent->rb_right;
				}

				// Case 4: 兄弟的右子是红色
				sibling->color = node->rb_parent->color;
				node->rb_parent->color = BLACK;
				sibling->rb_right->color = BLACK;
				rb_rotate_left(node->rb_parent, root);
				node = root->rb_node;
			}
		} else { // node 是右子节点，逻辑对称
			sibling = node->rb_parent->rb_left;

			if (sibling && sibling->color == RED) {
				sibling->color = BLACK;
				node->rb_parent->color = RED;
				rb_rotate_right(node->rb_parent, root);
				sibling = node->rb_parent->rb_left;
			}

			if ((!sibling->rb_right ||
			     sibling->rb_right->color == BLACK) &&
			    (!sibling->rb_left ||
			     sibling->rb_left->color == BLACK)) {
				sibling->color = RED;
				node = node->rb_parent;
			} else {
				if (!sibling->rb_left ||
				    sibling->rb_left->color == BLACK) {
					sibling->rb_right->color = BLACK;
					sibling->color = RED;
					rb_rotate_left(sibling, root);
					sibling = node->rb_parent->rb_left;
				}

				sibling->color = node->rb_parent->color;
				node->rb_parent->color = BLACK;
				sibling->rb_left->color = BLACK;
				rb_rotate_right(node->rb_parent, root);
				node = root->rb_node;
			}
		}
	}

	if (node)
		node->color = BLACK;
}

/**
 * 红黑树删除
 */
void rb_erase(struct rb_node *node, struct rb_root *root)
{
	struct rb_node *successor, *fixup;
	int original_color = node->color;

	if (!node->rb_left) { // 没有左子节点
		fixup = node->rb_right;
		rb_transplant(root, node, node->rb_right);
	} else if (!node->rb_right) { // 没有右子节点
		fixup = node->rb_left;
		rb_transplant(root, node, node->rb_left);
	} else { // 有两个子节点，找到后继节点
		successor = node->rb_right;
		while (successor->rb_left)
			successor = successor->rb_left;

		original_color = successor->color;
		fixup = successor->rb_right;

		if (successor->rb_parent == node) {
			if (fixup)
				fixup->rb_parent = successor;
		} else {
			rb_transplant(root, successor, successor->rb_right);
			successor->rb_right = node->rb_right;
			successor->rb_right->rb_parent = successor;
		}

		rb_transplant(root, node, successor);
		successor->rb_left = node->rb_left;
		successor->rb_left->rb_parent = successor;
		successor->color = node->color;
	}

	free(node); // 释放被删除的节点

	if (original_color == BLACK) // 只有删除黑色节点时，才需要修正
		rb_erase_fixup(root, fixup);
}

// 查找节点
struct rb_node *rb_search(const struct rb_root *root, int key)
{
	struct rb_node *node = root->rb_node;
	while (node) {
		struct my_rbnode *entry =
			container_of(node, struct my_rbnode, node);
		printf("Searching key: %d, current node: %d\n", key,
		       entry->data);
		if (key < entry->data)
			node = node->rb_left;
		else if (key > entry->data)
			node = node->rb_right;
		else
			return node;
	}

	return NULL;
}

void print_rb_tree(struct rb_node *node, int depth)
{
	if (!node)
		return;

	struct my_rbnode *entry = container_of(node, struct my_rbnode, node);
	print_rb_tree(node->rb_left, depth + 1);
	printf("Depth: %d, Key: %d\n", depth, entry->data);
	print_rb_tree(node->rb_right, depth + 1);
}
