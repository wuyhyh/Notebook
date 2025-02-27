/******************************************************************************
 *
 * Name: lru.c - Description
 * Created on 2025/02/21
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "lru.h"
#include "hash.h"
#include <stdlib.h>

static struct lru_node *create_node(int key, int value)
{
	struct lru_node *node = malloc(sizeof(struct lru_node));
	if (node == NULL) {
		return NULL;
	}

	node->key = key;
	node->value = value;
	node->prev = node->next = NULL;

	return node;
}

struct lru_cache *lru_cache_create(int capacity)
{
	struct lru_cache *cache = malloc(sizeof(struct lru_cache));
	if (cache == NULL) {
		return NULL;
	}

	cache->capacity = capacity;
	cache->size = 0;

	// 初始化哈希表
	cache->hash_table = calloc(HASH_SIZE, sizeof(struct lru_node *));
	if (cache->hash_table == NULL) {
		free(cache);
		return NULL;
	}

	// 创建 dummy head 和 dummy tail, 便于双向链表操作
	cache->head = create_node(0, 0);
	cache->tail = create_node(0, 0);
	if (cache->head == NULL || cache->tail == NULL) {
		free(cache->hash_table);
		free(cache);
		return NULL;
	}

	// 连接伪首部和伪尾部
	cache->head->next = cache->tail;
	cache->tail->prev = cache->head;

	return cache;
}

// 从双向链表中移除一个节点
static void remove_node(struct lru_node *node)
{
	node->prev->next = node->next;
	node->next->prev = node->prev;
}

// 将节点移动到尾部
static void add_to_tail(struct lru_cache *cache, struct lru_node *node)
{
	node->prev = cache->tail->prev;
	node->next = cache->tail;
	cache->tail->prev->next = node;
	cache->tail->prev = node;
}

// 淘汰最久未使用节点
static void evict_lru(struct lru_cache *cache)
{
	struct lru_node *lru = cache->head->next;
	if (lru == NULL) {
		return;
	}

	remove_node(lru);
	int lru_index = hash_function(lru->key);
	struct lru_node *prev = NULL, *curr = cache->hash_table[lru_index];

	while (curr) {
		if (curr == lru) {
			if (prev)
				prev->next = curr->next;
			else
				cache->hash_table[lru_index] = curr->next;
			free(curr);
			break;
		}
		prev = curr;
		curr = curr->next;
	}
	cache->size--;
}

// 插入新节点
static void insert_new_node(struct lru_cache *cache, int key, int value)
{
	struct lru_node *new_node = create_node(key, value);
	if (new_node == NULL) {
		return;
	}

	int index = hash_function(key);
	new_node->next = cache->hash_table[index];
	cache->hash_table[index] = new_node;

	add_to_tail(cache, new_node); // 移到最近使用
	cache->size++;
}

// 获取 LRU 缓存中的值
int lru_cache_get(struct lru_cache *cache, int key)
{
	int index = hash_function(key);
	struct lru_node *node = cache->hash_table[index];

	while (node) {
		if (node->key == key) {
			remove_node(node);
			add_to_tail(cache, node);
			return node->value;
		}
		node = node->next;
	}
	return -1;
}

// 插入或更新 LRU 缓存
void lru_cache_put(struct lru_cache *cache, int key, int value)
{
	int index = hash_function(key);
	struct lru_node *node = cache->hash_table[index];

	while (node) {
		if (node->key == key) {
			node->value = value;
			remove_node(node);
			add_to_tail(cache, node);
			return;
		}
		node = node->next;
	}

	// 如果缓存已满，淘汰 LRU 节点
	if (cache->size >= cache->capacity) {
		evict_lru(cache);
	}

	// 插入新节点
	insert_new_node(cache, key, value);
}

// 释放 LRU 缓存
void lru_cache_free(struct lru_cache *cache)
{
	struct lru_node *cur = cache->head;
	while (cur) {
		struct lru_node *tmp = cur;
		cur = cur->next;
		free(tmp);
	}
	free(cache->hash_table);
	free(cache);
}
