/******************************************************************************
 *
 * Name: reverse_list.c - Description
 * Created on 2025/02/23
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>

struct ListNode {
	int val;
	struct ListNode *next;
};

// 辅助函数 反转 K 个节点
struct ListNode *reverse_linked_list(struct ListNode *head, int k)
{
	struct ListNode *prev = NULL;
	struct ListNode *curr = head;
	struct ListNode *next = NULL;

	while (k--) {
		next = curr->next;
		curr->next = prev;
		prev = curr;
		curr = next;
	}

	return prev;
}

//  主函数 反转 K 个一组

struct ListNode *reverseKGroup(struct ListNode *head, int k)
{
	if (head == NULL || k == 1)
		return head;

	// 计算链表长度
	int length = 0;
	struct ListNode *tmp = head;
	while (tmp != NULL) {
		length++;
		tmp = tmp->next;
	}

	struct ListNode *dummy = malloc(sizeof(struct ListNode));
	dummy->next = head;
	struct ListNode *group_prev = dummy;

	while (length >= k) {
		struct ListNode *group_head = group_prev->next;
		struct ListNode *group_tail = group_head;
		for (int i = 0; i < k - 1; i++)
			group_tail = group_tail->next;
		struct ListNode *next_group = group_tail->next;

		// 反转当前 K 个节点
		group_tail->next = NULL;
		struct ListNode *reversed_head =
			reverse_linked_list(group_head, k);

		// 将反装后的链表连接到前后链表
		group_prev->next = reversed_head;
		group_head->next = next_group;
		group_prev = group_head;

		length -= k;
	}

	return dummy->next;
}

// 辅助函数 创建链表
struct ListNode *create_linked_list(int *arr, int size)
{
	struct ListNode *head = NULL;
	struct ListNode *tail = NULL;

	for (int i = 0; i < size; ++i) {
		struct ListNode *new_node = malloc(sizeof(struct ListNode));
		new_node->val = arr[i];
		new_node->next = NULL;
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

// 辅助函数 打印链表
void print_linked_list(struct ListNode *head)
{
	struct ListNode *walker = head;
	while (walker) {
		printf("%d ", walker->val);
		walker = walker->next;
	}
	printf("\n");
}

int main(void)
{
	int arr[] = { 1, 2, 3, 4, 5 };
	int k = 3;
	struct ListNode *head =
		create_linked_list(arr, sizeof(arr) / sizeof(int));
	printf("原链表: ");
	print_linked_list(head);
	struct ListNode *res = reverseKGroup(head, k);
	printf("反转后: ");
	print_linked_list(res);

	return 0;
}
