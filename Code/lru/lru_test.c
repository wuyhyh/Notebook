/******************************************************************************
*
 * Name: lru_test.c - Description
 * Created on 2025/02/21
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "lru.h"
#include <stdio.h>

int main(void)
{
        struct lru_cache *cache = lru_cache_create(2);

        lru_cache_put(cache, 1, 1);
        lru_cache_put(cache, 2, 2);
        printf("Get 1: %d\n", lru_cache_get(cache, 1));

        lru_cache_put(cache, 3, 3);
        printf("Get 2: %d\n", lru_cache_get(cache, 2));

        lru_cache_put(cache, 4, 4);
        printf("Get 1: %d\n", lru_cache_get(cache, 1));
        printf("Get 3: %d\n", lru_cache_get(cache, 3));
        printf("Get 4: %d\n", lru_cache_get(cache, 4));

        lru_cache_free(cache);

        return 0;
}
