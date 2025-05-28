/******************************************************************************
 *
 * Name: main.c - Description
 * Created on 2025/05/28
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>

#define SPI_CFG_CMD_RDID ((unsigned int)0x9F << 24)
#define SPI_CFG_DATA_TRANSFER (0x1 << 13)
#define SPI_CFG_CMD_THROUGH (0x1 << 21)
#define SPI_CFG_RW_NUM_3 (0x2 << 3)
#define PHYTIUM_CMD_SCK_SEL 0x07

void print_binary_groups(unsigned int num)
{
	for (int i = 31; i >= 0; i--) {
		printf("%d", (num >> i) & 1);
		if (i % 4 == 0 && i != 0)
			printf(" "); // 每4位加空格分隔
	}
	printf("\n");
}

int main()
{
	unsigned int cmd_value = 0;
	cmd_value = SPI_CFG_CMD_RDID | SPI_CFG_DATA_TRANSFER |
		    SPI_CFG_CMD_THROUGH | SPI_CFG_RW_NUM_3 |
		    PHYTIUM_CMD_SCK_SEL;

	printf("原始值: 0x%08X\n", cmd_value);
	printf("二进制分组: ");
	print_binary_groups(cmd_value);

	return 0;
}
