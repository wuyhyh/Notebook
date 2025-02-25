/******************************************************************************
 *
 * Name: queue.h - Description
 * Created on 2025/02/25
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef NOTEBOOK_QUEUE_H
#define NOTEBOOK_QUEUE_H

#include "tree.h"

// 队列节点
typedef struct QueueNode {
	TreeNode *node;
	unsigned long index;
	struct QueueNode *next;
} QueueNode;

// 队列结构
typedef struct Queue {
	QueueNode *front;
	QueueNode *rear;
} Queue;

Queue *create_queue();
void enqueue(Queue *q, TreeNode *node, unsigned long index);
void dequeue(Queue *q);
QueueNode *front(Queue *q);
int is_empty(Queue *q);
void free_queue(Queue *q);

#endif //NOTEBOOK_QUEUE_H
