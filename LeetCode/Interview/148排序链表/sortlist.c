/******************************************************************************
 *
 * Name: sortlist.c - Description
 * Created on 2025/03/01
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>

struct ListNode {
	int val;
	struct ListNode *next;
};

// 归并2个有序链表
struct ListNode *mergeTwoLists(struct ListNode *l1, struct ListNode *l2)
{
	struct ListNode dummy;
	struct ListNode *cur = &dummy;
	dummy.next = NULL;

	while (l1 != NULL && l2 != NULL) {
		if (l1->val < l2->val) {
			cur->next = l1;
			l1 = l1->next;
		} else {
			cur->next = l2;
			l2 = l2->next;
		}
		cur = cur->next;
	}

	// 处理剩余部分
	cur->next = l1 ? l1 : l2;
	return dummy.next;
}

// 使用快慢指针找到中间节点并拆分链表
struct ListNode *sortList(struct ListNode *head)
{
	// 递归终止条件
	if (!head || !head->next) {
		return head;
	}

	struct ListNode *slow = head;
	struct ListNode *fast = head->next;
	while (fast && fast->next) {
		slow = slow->next;
		fast = fast->next->next;
	}

	// 拆分链表
	struct ListNode *mid = slow->next;
	slow->next = NULL;

	// 递归排序左右两部分
	struct ListNode *left = sortList(head);
	struct ListNode *right = sortList(mid);

	// 归并排序后的两部分
	return mergeTwoLists(left, right);
}

// 创建新节点
struct ListNode *create_node(int val)
{
	struct ListNode *node =
		(struct ListNode *)malloc(sizeof(struct ListNode));
	node->val = val;
	node->next = NULL;
	return node;
}

// 打印链表
void print_list(struct ListNode *head)
{
	while (head) {
		printf("%d -> ", head->val);
		head = head->next;
	}
	printf("NULL\n");
}

// 释放链表内存
void free_list(struct ListNode *head)
{
	while (head) {
		struct ListNode *tmp = head;
		head = head->next;
		free(tmp);
	}
}

// 测试函数
int main(void)
{
	struct ListNode *head = create_node(4);
	head->next = create_node(2);
	head->next->next = create_node(1);
	head->next->next->next = create_node(3);

	printf("List before sorting:\n");
	print_list(head);

	head = sortList(head);

	printf("List after sorting:\n");
	print_list(head);

	free_list(head);

	return 0;
}
