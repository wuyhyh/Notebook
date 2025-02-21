CC = gcc
CFLAGS = -g -Wall -O0  # 开启调试信息
TARGET = stack_program  # 生成的可执行文件
SRCS = stack_client.c stackADT.c
OBJS = $(SRCS:.c=.o)

# Fedora Server 配置
REMOTE_USER = root      # 远程服务器用户名
REMOTE_HOST = 10.211.55.9  # 远程服务器 IP
REMOTE_DIR = /home/CLionProjects/Notebook/C_programming/Stack_example_of_ADT/stack_v5_link  # 远程项目目录

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

# 远程部署：将代码和可执行文件同步到 Fedora Server
deploy:
	rsync -avz --exclude '.*' ./ $(REMOTE_USER)@$(REMOTE_HOST):$(REMOTE_DIR)

# 远程运行 gdbserver
debug-server: deploy
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && gdbserver :1234 ./$(TARGET)"

