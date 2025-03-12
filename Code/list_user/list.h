/******************************************************************************
 *
 * Name: list.h - Description
 * Created on 2025/03/12
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef LIST_H
#define LIST_H

#include <stdio.h>
#include <stdlib.h>

struct list_head {
	struct list_head *next;
	struct list_head *prev;
};

#define LIST_NODE_INIT(name) { &(name), &(name) }

#define LIST_HEAD(name) struct list_head name = LIST_NODE_INIT(name)

static inline void INIT_LIST_HEAD(struct list_head *list)
{
	list->next = list;
	list->prev = list;
}

static inline void __list_add(struct list_head *new, struct list_head *prev,
			      struct list_head *next)
{
	prev->next = new;
	new->prev = prev;
	new->next = next;
	next->prev = new;
}

static inline void list_add(struct list_head *new, struct list_head *head)
{
	__list_add(new, head, head->next);
}

static inline void list_add_tail(struct list_head *new, struct list_head *head)
{
	__list_add(new, head->prev, head);
}

static inline void __list_del(struct list_head *prev, struct list_head *next)
{
	next->prev = prev;
	prev->next = next;
}

static inline void list_del(struct list_head *entry)
{
	__list_del(entry->prev, entry->next);
	entry->next = entry;
	entry->prev = entry;
}

static inline int list_empty(const struct list_head *head)
{
	return head->next == head;
}

#define list_for_each_safe(pos, n, head)                       \
	for (pos = (head)->next, n = pos->next; pos != (head); \
	     pos = n, n = pos->next)

#define list_for_each(pos, head) \
	for (pos = (head)->next; pos != (head); pos = pos->next)

/*
 * 获取包含该链表节点的结构体
 */
#define container_of(ptr, type, member) \
	((type *)((char *)(ptr) - (unsigned long)(&((type *)0)->member)))

#define list_for_each_entry(pos, head, member)                       \
	for (pos = container_of((head)->next, typeof(*pos), member); \
	     &pos->member != (head);                                 \
	     pos = container_of(pos->member.next, typeof(*pos), member))

#endif //LIST_H
