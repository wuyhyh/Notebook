
/******************************************************************************
 *
 * Name: test_width.c - Description
 * Created on 2025/02/25
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "width.h"
#include "tree.h"
#include <stdio.h>

int main(void)
{
	TreeNode *root = create_node(1);
	root->left = create_node(3);
	root->right = create_node(2);
	root->left->left = create_node(5);
	root->left->right = create_node(3);
	root->right->left = create_node(9);

	printf("max width of tree: %d\n", widthOfBinaryTree(root));

	free_tree(root);
	return 0;
}
