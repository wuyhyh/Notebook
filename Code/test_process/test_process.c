/******************************************************************************
 *
 * Name: test_process.c - Description
 * Created on 2025/04/20
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <unistd.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

void *thread_1(void *arg)
{
	while (1) {
		sleep(2);
		printf("thread 1\n");
	}
}

void *thread_2(void *arg)
{
	while (1) {
		sleep(2);
		printf("thread 2\n");
	}
}

int main(void)
{
	pid_t pid;
	pthread_t id_1, id_2;
	int ret;

	if ((pid = fork()) < 0) {
		return EXIT_FAILURE;
	} else if (pid == 0) {
		ret = pthread_create(&id_1, NULL, thread_1, NULL);
		if (ret != 0) {
			return EXIT_FAILURE;
		}
		ret = pthread_create(&id_2, NULL, thread_2, NULL);
		if (ret != 0) {
			return EXIT_FAILURE;
		}
		pthread_join(id_1, NULL);
		pthread_join(id_2, NULL);
	} else {
		while (1) {
			;
		}
	}

	return 0;
}