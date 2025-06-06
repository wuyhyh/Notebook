# Makefile for bitcmp

CC = gcc
CFLAGS = -O2 -Wall -pthread
TARGET = bitcmp
SRC = bitcmp.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)

