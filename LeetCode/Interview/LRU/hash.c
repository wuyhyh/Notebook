/******************************************************************************
 *
 * Name: hash.c - Description
 * Created on 2025/02/21
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include "hash.h"

int hash_function(int key)
{
	return key % HASH_SIZE;
}
