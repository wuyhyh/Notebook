/******************************************************************************
 *
 * Name: tree.h - Description
 * Created on 2025/02/25
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef NOTEBOOK_TREE_H
#define NOTEBOOK_TREE_H

typedef struct TreeNode {
	int val;
	struct TreeNode *left;
	struct TreeNode *right;
} TreeNode;

// 创建节点
TreeNode *create_node(int val);

// 释放二叉树
void free_tree(TreeNode *root);

#endif //NOTEBOOK_TREE_H
