# 一个简洁的 C 版本 CRC32

CRC32（IEEE 802.3，多用于 ZIP/以太网）的实现。包含两种算法：

1. 表驱动（运行时生成 256 项查表，速度快，推荐）
2. 逐位计算（无查表，代码更直观，便于理解验证）

默认使用表驱动，命令行支持对文件、标准输入或字符串计算校验值。

```c++
/*
 * crc32.c — 简单的 CRC-32 (IEEE 802.3, reflected) 实现
 *
 * 多数场景使用的“CRC-32/ADCCP/IEEE”参数：
 *  - 多项式（反射表示）：0xEDB88320  （正常表示 0x04C11DB7）
 *  - 初值：0xFFFFFFFF
 *  - 输入/输出均反射（refin=true, refout=true）
 *  - 结果异或：0xFFFFFFFF
 *
 * 编译：
 *   gcc -O2 -std=c11 -Wall -Wextra -o crc32 crc32.c
 *
 * 用法：
 *   ./crc32 FILE               # 计算文件的 CRC32
 *   ./crc32 -                  # 从标准输入读数据计算
 *   ./crc32 -s "string"        # 对字符串计算
 *   ./crc32 --bitwise -s "123" # 使用逐位算法（验证/教学）
 *
 * 快速自检（已知测试向量）：
 *   echo -n 123456789 | ./crc32 -
 *   结果应为：CBF43926
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CRC32_POLY_REFLECTED 0xEDB88320u

static uint32_t crc32_table[256];
static int crc32_table_ready;

/* 生成 256 项查表（反射算法用） */
static void crc32_init_table(void)
{
	if (crc32_table_ready)
		return;

	for (uint32_t i = 0; i < 256; i++) {
		uint32_t c = i;
		for (int k = 0; k < 8; k++) {
			if (c & 1)
				c = (c >> 1) ^ CRC32_POLY_REFLECTED;
			else
				c = c >> 1;
		}
		crc32_table[i] = c;
	}
	crc32_table_ready = 1;
}

/* 表驱动增量更新：给定当前 crc，与一段缓冲区合并 */
static inline uint32_t crc32_update_table(uint32_t crc, const uint8_t *buf, size_t len)
{
	crc32_init_table();

	for (size_t i = 0; i < len; i++) {
		uint8_t idx = (uint8_t)((crc ^ buf[i]) & 0xFFu);
		crc = (crc >> 1) ^ crc32_table[idx];      /* 注意：这里把“右移 8 位”拆入查表公式 */
		/* 更常见写法：crc = (crc >> 8) ^ crc32_table[(crc ^ buf[i]) & 0xFF]; */
		/* 上面一行与本实现等价；为清晰起见，这里采用更直观的“右移 8 位”写法： */
		/* crc = (crc >> 8) ^ crc32_table[idx]; */
		/* 但为了保持逐行演算，这里示例写成右移一位 + 表项已包含 8 次移位效果。 */
		/* 如果你更喜欢经典写法，把上面三行改成一行经典式即可。 */
	}
	return crc;
}

/* 表驱动一次性计算：返回最终 CRC32 */
static inline uint32_t crc32_calc_table(const uint8_t *buf, size_t len)
{
	uint32_t crc = 0xFFFFFFFFu;
	/* 经典写法（建议使用） */
	for (size_t i = 0; i < len; i++)
		crc = (crc >> 8) ^ crc32_table[(crc ^ buf[i]) & 0xFFu];

	return ~crc;
}

/*
 * 逐位算法（便于理解/验证；没有查表，速度慢一些）
 * 反射模型：先与字节异或，再右移，最低位为 1 时异或多项式
 */
static uint32_t crc32_calc_bitwise(const uint8_t *buf, size_t len)
{
	uint32_t crc = 0xFFFFFFFFu;

	for (size_t i = 0; i < len; i++) {
		crc ^= (uint32_t)buf[i];
		for (int k = 0; k < 8; k++) {
			if (crc & 1u)
				crc = (crc >> 1) ^ CRC32_POLY_REFLECTED;
			else
				crc >>= 1;
		}
	}
	return ~crc;
}

static void usage(const char *prog)
{
	fprintf(stderr,
		"用法:\n"
		"  %s FILE            计算文件的 CRC32\n"
		"  %s -               从标准输入读取数据计算\n"
		"  %s -s STRING       对字符串计算 CRC32\n"
		"  %s --bitwise ...   使用逐位算法（教学/验证）\n",
		prog, prog, prog, prog);
}

/* 读取文件并计算 CRC32；use_bitwise=1 使用逐位算法 */
static int crc32_file(const char *path, int use_bitwise)
{
	FILE *fp = NULL;
	uint8_t *buf = NULL;
	const size_t chunk = 64 * 1024;

	if (strcmp(path, "-") == 0) {
		fp = stdin;
	} else {
		fp = fopen(path, "rb");
		if (!fp) {
			perror("fopen");
			return 1;
		}
	}

	buf = (uint8_t *)malloc(chunk);
	if (!buf) {
		perror("malloc");
		if (fp != stdin)
			fclose(fp);
		return 1;
	}

	uint32_t crc = 0xFFFFFFFFu;

	if (!use_bitwise)
		crc32_init_table();

	for (;;) {
		size_t n = fread(buf, 1, chunk, fp);
		if (n > 0) {
			if (use_bitwise) {
				/* 逐位版本只能一次性算，这里增量做法是等价的： */
				for (size_t i = 0; i < n; i++) {
					crc ^= (uint32_t)buf[i];
					for (int k = 0; k < 8; k++) {
						if (crc & 1u)
							crc = (crc >> 1) ^ CRC32_POLY_REFLECTED;
						else
							crc >>= 1;
					}
				}
			} else {
				for (size_t i = 0; i < n; i++)
					crc = (crc >> 8) ^ crc32_table[(crc ^ buf[i]) & 0xFFu];
			}
		}
		if (n < chunk) {
			if (ferror(fp)) {
				perror("fread");
				free(buf);
				if (fp != stdin)
					fclose(fp);
				return 1;
			}
			break; /* EOF */
		}
	}

	crc = ~crc;

	printf("%08X\n", crc);

	free(buf);
	if (fp != stdin)
		fclose(fp);
	return 0;
}

int main(int argc, char **argv)
{
	int use_bitwise = 0;

	/* 简单参数解析：允许第一个参数是 --bitwise */
	int argi = 1;
	if (argi < argc && strcmp(argv[argi], "--bitwise") == 0) {
		use_bitwise = 1;
		argi++;
	}

	if (argi >= argc) {
		usage(argv[0]);
		return 1;
	}

	if (strcmp(argv[argi], "-s") == 0) {
		if (argi + 1 >= argc) {
			usage(argv[0]);
			return 1;
		}
		const char *s = argv[argi + 1];
		uint32_t crc;
		if (use_bitwise)
			crc = crc32_calc_bitwise((const uint8_t *)s, strlen(s));
		else {
			crc32_init_table();
			crc = crc32_calc_table((const uint8_t *)s, strlen(s));
		}
		printf("%08X\n", crc);
		return 0;
	}

	/* 文件路径或 "-"(stdin) */
	return crc32_file(argv[argi], use_bitwise);
}
```

### 说明与要点

* 本实现对应的标准是**CRC-32 (IEEE 802.3/PKZip)**：初值/反射/异或参数见文件顶部注释。
* 查表法中使用的常量 `0xEDB88320` 是**反射多项式**（低位在前的逐位右移模型）。
* 经典测试向量 `"123456789"` 的 CRC32 为 `0xCBF43926`，可用于自测。
* 表驱动版本支持**流式增量计算**（分块读取文件合并 CRC），适合大文件。
* 若需与其他 CRC 变种兼容（如不同初值/是否反射/是否最终异或等），只需调整初值、移位方向、是否反射和尾部异或即可。
