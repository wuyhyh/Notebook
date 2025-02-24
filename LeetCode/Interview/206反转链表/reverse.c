/******************************************************************************
 *
 * Name: reverse.c - Description
 * Created on 2025/02/24
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdlib.h>
#include <stdio.h>

struct ListNode {
	int val;
	struct ListNode *next;
};

// 反转链表函数
struct ListNode *reverseList(struct ListNode *head)
{
	struct ListNode *prev = NULL;
	struct ListNode *curr = head;
	struct ListNode *next_tmp = NULL;

	while (curr != NULL) {
		next_tmp = curr->next;
		curr->next = prev;
		prev = curr;
		curr = next_tmp;
	}

	return prev;
}

// 辅助函数 打印链表
void print_list(struct ListNode *head)
{
	struct ListNode *walker = head;

	while (walker != NULL) {
		printf("%d -> ", walker->val);
		walker = walker->next;
	}
	printf("\n");
}

// 辅助函数，创建一个新的链表节点
static struct ListNode *create_node(int val)
{
	struct ListNode *new_node = malloc(sizeof(struct ListNode));
	new_node->val = val;
	new_node->next = NULL;
	return new_node;
}

// 辅助函数 创建一个链表
struct ListNode *create_list(int arr[], int n)
{
	struct ListNode *head = NULL;
	struct ListNode *tail = NULL;

	for (int i = 0; i < n; i++) {
		struct ListNode *new_node = create_node(arr[i]);
		if (head == NULL) {
			head = new_node;
			tail = new_node;
		} else {
			tail->next = new_node;
			tail = new_node;
		}
	}

	return head;
}

int main(void)
{
	int a[] = { 1, 2, 3, 4, 5 };
	struct ListNode *head = create_list(a, 5);

	printf("Original:\n");
	print_list(head);
	head = reverseList(head);
	printf("Result:\n");
	print_list(head);

	return 0;
}
