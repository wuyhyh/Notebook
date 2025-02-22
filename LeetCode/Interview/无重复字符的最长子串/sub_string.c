/******************************************************************************
 *
 * Name: sub_string.c - Description
 * Created on 2025/02/22
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <string.h>

int lengthOfLongestSubstring(char *s)
{
	int char_index[128] = { 0 };
	int left = 0;
	int max_length = 0;

	for (int right = 0; s[right] != '\0'; right++) {
		if (char_index[s[right]] > left) {
			left = char_index[s[right]]; // 右移左指针
		}
		char_index[s[right]] = right + 1;
		int curr_length = right - left + 1;
		if (curr_length > max_length) {
			max_length = curr_length;
		}
	}

	return max_length;
}

int main(void)
{
	char s[] = "abcabcbb";
	printf("%d\n", lengthOfLongestSubstring(s));
	return 0;
}
