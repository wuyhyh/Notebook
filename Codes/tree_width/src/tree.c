/******************************************************************************
 *
 * Name: tree.c - Description
 * Created on 2025/02/25
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "tree.h"
#include <stdio.h>
#include <stdlib.h>

TreeNode *create_node(int val)
{
	TreeNode *node = malloc(sizeof(TreeNode));
	if (node == NULL) {
		printf("error\n");
		exit(EXIT_FAILURE);
	}

	node->val = val;
	node->left = NULL;
	node->right = NULL;

	return node;
}

void free_tree(TreeNode *root)
{
	if (root == NULL)
		return;

	free_tree(root->left);
	free_tree(root->right);
	free(root);
}
