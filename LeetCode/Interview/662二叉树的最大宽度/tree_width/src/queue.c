/******************************************************************************
 *
 * Name: queue.c - Description
 * Created on 2025/02/25
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "queue.h"
#include <stdlib.h>
#include <stdio.h>

Queue *create_queue()
{
	Queue *q = malloc(sizeof(Queue));
	if (!q) {
		printf("error\n");
		exit(EXIT_FAILURE);
	}

	q->front = NULL;
	q->rear = NULL;

	return q;
}

void enqueue(Queue *q, TreeNode *node, unsigned long index)
{
	QueueNode *tmp = malloc(sizeof(QueueNode));
	if (!tmp) {
		printf("error\n");
		exit(EXIT_FAILURE);
	}

	tmp->node = node;
	tmp->index = index;
	tmp->next = NULL;

	if (q->rear == NULL) {
		q->front = q->rear = tmp;
		return;
	}
	q->rear->next = tmp;
	q->rear = tmp;
}

void dequeue(Queue *q)
{
	if (q->front == NULL) {
		return;
	}

	QueueNode *tmp = q->front;
	q->front = q->front->next;
	if (q->front == NULL) {
		q->rear = NULL;
	}
	free(tmp);
}

QueueNode *front(Queue *q)
{
	return q->front;
}

int is_empty(Queue *q)
{
	return q->front == NULL;
}

void free_queue(Queue *q)
{
	while (!q) {
		dequeue(q);
	}
	free(q);
}
