/******************************************************************************
 *
 * Name: read_spi.c - Description
 * Created on 2025/06/09
 * Copyright (C) 2022 - 2025, wyh.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/spi/spidev.h>
#include <sys/ioctl.h>
#include <string.h>
#include <errno.h>

#define SPI_DEV "/dev/spidev0.0"
#define CMD_RDSR 0x05 // Read Status Register 1

int main()
{
	int fd = open(SPI_DEV, O_RDWR);
	if (fd < 0) {
		perror("open spidev");
		return 1;
	}

	uint8_t mode = SPI_MODE_0;
	uint8_t bits = 8;
	uint32_t speed = 500000; // 500kHz

	ioctl(fd, SPI_IOC_WR_MODE, &mode);
	ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits);
	ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed);

	uint8_t tx[2] = { CMD_RDSR, 0x00 };
	uint8_t rx[2] = { 0 };

	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)rx,
		.len = 2,
		.delay_usecs = 0,
		.speed_hz = speed,
		.bits_per_word = bits,
	};

	int ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
	if (ret < 1) {
		perror("SPI_IOC_MESSAGE failed");
		close(fd);
		return 1;
	}

	printf("SR1 = 0x%02X\n", rx[1]);
	printf("Status bits:\n");
	printf("  WIP = %d\n", rx[1] & 0x01);
	printf("  WEL = %d\n", (rx[1] >> 1) & 0x01);
	printf("  BP  = 0x%X\n", (rx[1] >> 2) & 0x0F);
	printf("  TB  = %d\n", (rx[1] >> 6) & 0x01);
	printf("  SRP = %d\n", (rx[1] >> 7) & 0x01);

	close(fd);
	return 0;
}
