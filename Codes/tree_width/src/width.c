/******************************************************************************
 *
 * Name: width.c - Description
 * Created on 2025/02/25
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "width.h"
#include "queue.h"
#include <stdio.h>
#include <stdlib.h>

static int queue_size(Queue *q)
{
	if (q == NULL || q->front == NULL)
		return 0;

	int count = 0;
	QueueNode *tmp = q->front;
	while (tmp) {
		count++;
		tmp = tmp->next;
	}

	return count;
}

int widthOfBinaryTree(TreeNode *root)
{
	if (!root)
		return 0;

	Queue *queue = create_queue();
	enqueue(queue, root, 0);
	int max_width = 0;

	while (!is_empty(queue)) {
		int size = queue_size(queue);
		unsigned long min_index = front(queue)->index;
		unsigned long first, last;

		for (int i = 0; i < size; i++) {
			QueueNode *q_node = front(queue);
			dequeue(queue);
			TreeNode *t_node = q_node->node;
			unsigned long index = q_node->index - min_index;

			if (i == 0)
				first = index;
			if (i == size - 1)
				last = index;

			if (t_node->left)
				enqueue(queue, t_node->left, 2 * index);
			if (t_node->right)
				enqueue(queue, t_node->right, 2 * index + 1);
		}

		max_width = (last - first + 1) > max_width ?
				    (last - first + 1) :
				    max_width;
	}

	free_queue(queue);
	return max_width;
}
