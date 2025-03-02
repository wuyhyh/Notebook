/******************************************************************************
 *
 * Name: right_view.c - Description
 * Created on 2025/03/02
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>

struct tree_node {
	int val;
	struct tree_node *left;
	struct tree_node *right;
};

struct queue_node {
	struct tree_node *tree;
	struct queue_node *next;
};

// 队列
struct queue {
	struct queue_node *front;
	struct queue_node *rear;
};

// 初始化队列
static struct queue *queue_init(void)
{
	struct queue *queue = (struct queue *)malloc(sizeof(struct queue));
	if (queue == NULL)
		return NULL;

	queue->front = queue->rear = NULL;
	return queue;
}

static void queue_enqueue(struct queue *queue, struct tree_node *node)
{
	struct queue_node *new_node =
		(struct queue_node *)malloc(sizeof(struct queue_node));
	if (new_node == NULL)
		return;
	new_node->tree = node;
	new_node->next = NULL;

	// 如果队列为空，新节点就是头部也是尾部
	if (queue->rear == NULL) {
		queue->front = queue->rear = new_node;
	} else {
		queue->rear->next = new_node;
		queue->rear = new_node;
	}
}

static struct tree_node *queue_dequeue(struct queue *queue)
{
	// 队列为空
	if (queue->front == NULL)
		return NULL;

	// 存储front中的值，并且更新front
	struct queue_node *temp = queue->front;
	struct tree_node *tree = temp->tree;
	queue->front = queue->front->next;

	// 如果取出后队列为空，rear也要更新为空
	if (queue->front == NULL)
		queue->rear = NULL;

	free(temp);
	return tree;
}

// 检查队列是否为空
static int queue_empty(struct queue *queue)
{
	return queue->front == NULL;
}

// 释放整个队列的内存
static void free_queue(struct queue *queue)
{
	while (!queue_empty(queue)) {
		queue_dequeue(queue);
	}
	free(queue);
}

// 右视图节点数组
struct result_array {
	int *data;
	int size;
};

// 计算二叉树的右视图
static void right_side_view(struct tree_node *root,
			     struct result_array *result)
{
	if (root == NULL)
		return;

	struct queue *queue = queue_init();
	if (queue == NULL)
		return;

	// 将根节点入队
	queue_enqueue(queue, root);

	while (!queue_empty(queue)) {
		int level_size = 0;
		struct queue_node *temp = queue->front;

		// 计算当前层的节点数
		while (temp != NULL) {
			level_size++;
			temp = temp->next;
		}

		// 遍历当前层所有的节点
		for (int i = 0; i < level_size; i++) {
			struct tree_node *node = queue_dequeue(queue);

			// 记录当前层的最后一个节点
			if (i == level_size - 1)
				result->data[result->size++] = node->val;

			// 左子树 右子树 入队
			if (node->left != NULL)
				queue_enqueue(queue, node->left);
			if (node->right != NULL)
				queue_enqueue(queue, node->right);
		}
	}

	// 释放队列
	free_queue(queue);
}

// 创建新的二叉树节点
static struct tree_node *new_node(int val)
{
	struct tree_node *node =
		(struct tree_node *)malloc(sizeof(struct tree_node));
	if (node == NULL)
		return NULL;

	node->val = val;
	node->left = NULL;
	node->right = NULL;
	return node;
}

// 释放二叉树的内存
static void free_tree(struct tree_node *root)
{
	if (root == NULL)
		return;

	free_tree(root->left);
	free_tree(root->right);
	free(root);
}

// 测试函数
int main(void)
{
	// 构造二叉树
	struct tree_node *root = new_node(1);
	root->left = new_node(2);
	root->right = new_node(3);
	root->left->right = new_node(5);
	root->right->right = new_node(4);

	// 结果数组
	struct result_array result;
	int data[100];
	result.data = data;
	result.size = 0;

	right_side_view(root, &result);

	// 输出结果
	printf("Right side view:\n");
	for (int i = 0; i < result.size; i++)
		printf("%d ", result.data[i]);
	printf("\n");

	// 释放二叉树
	free_tree(root);

	return 0;
}
