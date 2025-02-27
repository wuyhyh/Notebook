CC = gcc
CFLAGS = -Wall -g
TARGET = stack_client

all: $(TARGET)

$(TARGET): stack_client.o stackADT.o
	$(CC) $(CFLAGS) -o $(TARGET) stack_client.o stackADT.o

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o $(TARGET)
