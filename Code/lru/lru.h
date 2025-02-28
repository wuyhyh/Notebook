/******************************************************************************
*
 * Name: lru.h - Description
 * Created on 2025/02/21
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#ifndef NOTEBOOK_LRU_H
#define NOTEBOOK_LRU_H

// LRU 缓存节点
struct lru_node
{
        int key;
        int value;
        struct lru_node *prev, *next;
};

// LRU 缓存结构
struct lru_cache
{
        int capacity;
        int size;
        struct lru_node *head, *tail;
        struct lru_node** hash_table;
};

// 初始化 LRU 缓存
struct lru_cache* lru_cache_create(int capacity);

// 获取缓存值
int lru_cache_get(struct lru_cache* cache, int key);

// 插入或更新缓存
void lru_cache_put(struct lru_cache* cache, int key, int value);

// 释放 LRU 缓存
void lru_cache_free(struct lru_cache* cache);

#endif //NOTEBOOK_LRU_H
