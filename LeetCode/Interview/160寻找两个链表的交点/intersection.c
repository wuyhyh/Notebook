/******************************************************************************
 *
 * Name: intersection.c - Description
 * Created on 2025/02/28
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>

struct ListNode {
	int val;
	struct ListNode *next;
};

struct ListNode *getIntersectionNode(struct ListNode *headA,
				     struct ListNode *headB)
{
	if (!headA || !headB)
		return NULL;

	struct ListNode *a = headA;
	struct ListNode *b = headB;

	// 当 a = b 时，说明找到交点，如果二者最后都为 NULL，说明没有交点
	while (a != b) {
		a = ((a == NULL) ? headB : a->next);
		b = ((b == NULL) ? headA : b->next);
	}

	return a;
}
