/******************************************************************************
 *
 * Name: bitcmp.c - Description
 * Created on 2025/06/06
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>

#define NUM_THREADS 4
#define PROGRESS_INTERVAL_MS 200  // 进度显示刷新时间，毫秒

typedef struct {
	uint8_t *buf1;
	uint8_t *buf2;
	size_t start;
	size_t end;
	size_t bit_diff;
} ThreadArg;

volatile size_t total_processed = 0;
size_t file_size = 0;
volatile int done = 0;

// 统计一个字节中置1的比特数
int count_bits(uint8_t byte)
{
	int count = 0;
	while (byte) {
		count++;
		byte &= (byte - 1);
	}
	return count;
}

// 子线程：执行比特比较
void *compare_bits(void *arg)
{
	ThreadArg *targ = (ThreadArg *)arg;
	size_t diff = 0;

	for (size_t i = targ->start; i < targ->end; i++) {
		uint8_t xor = targ->buf1[i] ^ targ->buf2[i];
		diff += count_bits(xor);
		__sync_fetch_and_add(&total_processed, 1); // 原子增加处理计数
	}

	targ->bit_diff = diff;
	return NULL;
}

// 进度监视线程
void *progress_monitor(void *arg)
{
	(void)arg;
	while (!done) {
		usleep(PROGRESS_INTERVAL_MS * 1000); // 毫秒
		size_t processed = total_processed;
		double percent = (double)processed / file_size * 100.0;
		printf("\rProgress: %.1f%% (%zu / %zu bytes)   ", percent,
		       processed, file_size);
		fflush(stdout);
	}
	// 最后打印100%
	printf("\rProgress: 100.0%% (%zu / %zu bytes)\n", file_size, file_size);
	return NULL;
}

int main(int argc, char *argv[])
{
	if (argc != 3) {
		fprintf(stderr, "Usage: %s <file1> <file2>\n", argv[0]);
		return EXIT_FAILURE;
	}

	FILE *f1 = fopen(argv[1], "rb");
	FILE *f2 = fopen(argv[2], "rb");
	if (!f1 || !f2) {
		perror("Error opening files");
		return EXIT_FAILURE;
	}

	struct stat st1, st2;
	fstat(fileno(f1), &st1);
	fstat(fileno(f2), &st2);

	if (st1.st_size != st2.st_size) {
		fprintf(stderr, "Error: Files are not the same size\n");
		return EXIT_FAILURE;
	}

	file_size = st1.st_size;
	uint8_t *buf1 = malloc(file_size);
	uint8_t *buf2 = malloc(file_size);
	if (!buf1 || !buf2) {
		perror("Memory allocation failed");
		return EXIT_FAILURE;
	}

	fread(buf1, 1, file_size, f1);
	fread(buf2, 1, file_size, f2);
	fclose(f1);
	fclose(f2);

	// 启动进度线程
	pthread_t progress_thread;
	pthread_create(&progress_thread, NULL, progress_monitor, NULL);

	// 启动比较线程
	pthread_t threads[NUM_THREADS];
	ThreadArg args[NUM_THREADS];
	size_t chunk = file_size / NUM_THREADS;

	for (int i = 0; i < NUM_THREADS; i++) {
		args[i].buf1 = buf1;
		args[i].buf2 = buf2;
		args[i].start = i * chunk;
		args[i].end = (i == NUM_THREADS - 1) ?
			              file_size :
			              (i + 1) * chunk;
		args[i].bit_diff = 0;
		pthread_create(&threads[i], NULL, compare_bits, &args[i]);
	}

	size_t total_diff = 0;
	for (int i = 0; i < NUM_THREADS; i++) {
		pthread_join(threads[i], NULL);
		total_diff += args[i].bit_diff;
	}

	done = 1;
	pthread_join(progress_thread, NULL);

	printf("Differing bits: %zu\n", total_diff);

	free(buf1);
	free(buf2);
	return EXIT_SUCCESS;
}
