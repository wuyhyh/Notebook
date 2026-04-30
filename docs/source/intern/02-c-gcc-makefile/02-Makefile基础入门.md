# 02-Makefile基础入门

## 1 文档目标

本文用于帮助实习生掌握 Makefile 的基础用法。

学习完本文后，应能够：

1. 理解为什么需要 Makefile。
2. 看懂最基本的 Makefile 规则。
3. 使用 `make` 编译简单 C 项目。
4. 理解目标、依赖、命令三者的关系。
5. 使用变量简化编译命令。
6. 编写一个简单的多文件 C 项目 Makefile。

## 2 为什么需要 Makefile

## 2.1 手动编译的问题

单个 C 文件可以直接编译：

```bash
gcc main.c -o app
```

但如果项目有多个文件：

```text
main.c
led.c
uart.c
gpio.c
```

手动编译会变得很麻烦：

```bash
gcc -g -O0 -Wall -Wextra main.c led.c uart.c gpio.c -o app
```

当文件越来越多时，手动输入命令容易出错，也不方便维护。

## 2.2 Makefile 的作用

Makefile 用来描述项目如何编译。

有了 Makefile 后，只需要执行：

```bash
make
```

就可以自动完成编译。

如果要清理编译结果，可以执行：

```bash
make clean
```

Makefile 的价值是：

1. 固化编译命令。
2. 减少重复输入。
3. 支持增量编译。
4. 便于多人协作。
5. 便于后续接入交叉编译和自动化构建。

## 3 最简单的 Makefile

## 3.1 示例项目

项目中只有一个文件：

```text
main.c
```

内容：

```c
#include <stdio.h>

int main(void)
{
    printf("hello make\n");
    return 0;
}
```

## 3.2 Makefile 示例

创建文件：

```text
Makefile
```

内容：

```text
app: main.c
	gcc main.c -o app
```

注意：第二行命令前面必须是 Tab，不是普通空格。

## 3.3 执行 make

执行：

```bash
make
```

make 会根据 Makefile 执行：

```bash
gcc main.c -o app
```

生成：

```text
app
```

运行：

```bash
./app
```

## 4 Makefile 基本规则

## 4.1 规则格式

Makefile 中最核心的格式是：

```text
目标: 依赖
	命令
```

例如：

```text
app: main.c
	gcc main.c -o app
```

含义：

1. `app` 是目标。
2. `main.c` 是依赖。
3. `gcc main.c -o app` 是生成目标的命令。

## 4.2 目标

目标通常是要生成的文件。

例如：

```text
app
main.o
led.o
```

也可以是一个动作名：

```text
clean
all
install
```

## 4.3 依赖

依赖表示生成目标需要哪些文件。

示例：

```text
app: main.o led.o
```

表示生成 `app` 需要：

1. `main.o`
2. `led.o`

如果依赖文件更新了，make 会重新生成目标。

## 4.4 命令

命令是真正执行的 shell 命令。

示例：

```text
	gcc main.o led.o -o app
```

注意：

1. 命令行必须以 Tab 开头。
2. 不是空格。
3. 这是 Makefile 初学最常见错误之一。

## 5 多文件项目 Makefile

## 5.1 示例项目结构

```text
project/
├── Makefile
├── main.c
├── led.c
└── led.h
```

`led.h`：

```c
#ifndef LED_H
#define LED_H

int led_init(void);
int led_set(int value);

#endif
```

`led.c`：

```c
#include "led.h"

int led_init(void)
{
    return 0;
}

int led_set(int value)
{
    return 0;
}
```

`main.c`：

```c
#include "led.h"

int main(void)
{
    led_init();
    led_set(1);

    return 0;
}
```

## 5.2 直接编译的 Makefile

```text
app: main.c led.c
	gcc -g -O0 -Wall -Wextra main.c led.c -o app
```

执行：

```bash
make
```

这种写法简单，适合很小的练习项目。

## 5.3 分步编译的 Makefile

更推荐写成：

```text
app: main.o led.o
	gcc main.o led.o -o app

main.o: main.c led.h
	gcc -g -O0 -Wall -Wextra -c main.c -o main.o

led.o: led.c led.h
	gcc -g -O0 -Wall -Wextra -c led.c -o led.o
```

执行：

```bash
make
```

编译流程：

1. `main.c` 编译成 `main.o`。
2. `led.c` 编译成 `led.o`。
3. `main.o` 和 `led.o` 链接成 `app`。

## 5.4 增量编译

如果只修改了 `led.c`，再次执行：

```bash
make
```

make 通常只会重新编译：

```text
led.o
app
```

不会重新编译 `main.o`。

这就是增量编译。

## 6 使用变量简化 Makefile

## 6.1 定义变量

Makefile 中可以定义变量：

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
```

使用变量：

```text
$(CC) $(CFLAGS) main.c -o $(TARGET)
```

## 6.2 使用变量后的 Makefile

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app

$(TARGET): main.o led.o
	$(CC) main.o led.o -o $(TARGET)

main.o: main.c led.h
	$(CC) $(CFLAGS) -c main.c -o main.o

led.o: led.c led.h
	$(CC) $(CFLAGS) -c led.c -o led.o
```

好处：

1. 编译器统一配置。
2. 编译选项统一配置。
3. 修改输出文件名更方便。
4. 后续改成交叉编译更容易。

## 6.3 常见变量名

常见变量：

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
LDFLAGS =
TARGET = app
OBJS = main.o led.o
```

含义：

1. `CC`：C 编译器。
2. `CFLAGS`：C 编译选项。
3. `LDFLAGS`：链接选项。
4. `TARGET`：最终目标文件。
5. `OBJS`：目标文件列表。

## 7 使用 OBJS 变量

## 7.1 改进 Makefile

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
OBJS = main.o led.o

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

main.o: main.c led.h
	$(CC) $(CFLAGS) -c main.c -o main.o

led.o: led.c led.h
	$(CC) $(CFLAGS) -c led.c -o led.o
```

如果以后增加 `uart.o`，只需要修改：

```text
OBJS = main.o led.o uart.o
```

## 7.2 链接选项

如果需要链接库，可以加 `LDFLAGS`：

```text
LDFLAGS = -lm
```

链接时使用：

```text
$(CC) $(OBJS) $(LDFLAGS) -o $(TARGET)
```

例如使用数学库时：

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
LDFLAGS = -lm
TARGET = app
OBJS = main.o calc.o

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(LDFLAGS) -o $(TARGET)
```

## 8 clean 目标

## 8.1 为什么需要 clean

编译后会生成：

```text
app
main.o
led.o
```

如果想清理这些文件，可以手动删除：

```bash
rm -f app main.o led.o
```

更常见的是在 Makefile 中写 `clean` 目标。

## 8.2 clean 示例

```text
clean:
	rm -f app main.o led.o
```

执行：

```bash
make clean
```

## 8.3 使用变量的 clean

```text
clean:
	rm -f $(TARGET) $(OBJS)
```

完整示例：

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
OBJS = main.o led.o

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

main.o: main.c led.h
	$(CC) $(CFLAGS) -c main.c -o main.o

led.o: led.c led.h
	$(CC) $(CFLAGS) -c led.c -o led.o

clean:
	rm -f $(TARGET) $(OBJS)
```

## 9 伪目标 .PHONY

## 9.1 什么是伪目标

`clean` 不是一个真正要生成的文件，而是一个动作。

建议声明为伪目标：

```text
.PHONY: clean
```

完整写法：

```text
.PHONY: clean

clean:
	rm -f $(TARGET) $(OBJS)
```

## 9.2 为什么要写 .PHONY

如果目录中刚好有一个文件叫 `clean`，执行：

```bash
make clean
```

make 可能会认为 `clean` 目标已经存在，不执行清理命令。

加上：

```text
.PHONY: clean
```

可以明确告诉 make：`clean` 是动作，不是文件。

## 10 默认目标 all

## 10.1 什么是默认目标

执行：

```bash
make
```

时，make 默认执行 Makefile 中第一个目标。

常见做法是把 `all` 放在第一个目标：

```text
all: $(TARGET)
```

## 10.2 完整示例

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
OBJS = main.o led.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

main.o: main.c led.h
	$(CC) $(CFLAGS) -c main.c -o main.o

led.o: led.c led.h
	$(CC) $(CFLAGS) -c led.c -o led.o

clean:
	rm -f $(TARGET) $(OBJS)
```

执行：

```bash
make
```

等价于：

```bash
make all
```

## 11 自动变量

## 11.1 常见自动变量

Makefile 中有一些常见自动变量：

```text
$@  表示目标文件
$<  表示第一个依赖文件
$^  表示所有依赖文件
```

注意：这些符号只在 Makefile 命令中使用。

## 11.2 自动变量示例

```text
app: main.o led.o
	gcc $^ -o $@
```

含义：

1. `$@` 表示 `app`。
2. `$^` 表示 `main.o led.o`。

等价于：

```text
app: main.o led.o
	gcc main.o led.o -o app
```

编译目标文件：

```text
main.o: main.c led.h
	gcc -c $< -o $@
```

含义：

1. `$@` 表示 `main.o`。
2. `$<` 表示第一个依赖 `main.c`。

## 12 模式规则

## 12.1 为什么需要模式规则

如果项目中有很多 `.c` 文件，每个 `.o` 都手写规则会很麻烦。

例如：

```text
main.o: main.c
	gcc -c main.c -o main.o

led.o: led.c
	gcc -c led.c -o led.o

uart.o: uart.c
	gcc -c uart.c -o uart.o
```

可以用模式规则简化。

## 12.2 模式规则示例

```text
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```

含义：

1. 任意 `.o` 文件可以由同名 `.c` 文件生成。
2. `$<` 是输入的 `.c` 文件。
3. `$@` 是输出的 `.o` 文件。

## 12.3 使用模式规则的完整 Makefile

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
OBJS = main.o led.o uart.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $^ -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJS)
```

这个 Makefile 已经可以支持多个 `.c` 文件的基本项目。

## 13 头文件依赖问题

## 13.1 为什么要关心头文件依赖

如果 `main.c` 包含 `led.h`：

```c
#include "led.h"
```

当 `led.h` 修改后，`main.o` 也应该重新编译。

手写规则时可以写：

```text
main.o: main.c led.h
```

但文件多了以后，手写头文件依赖很麻烦。

## 13.2 简单阶段怎么处理

初学阶段可以先手动写关键头文件依赖：

```text
main.o: main.c led.h
led.o: led.c led.h
```

先理解基本机制。

后续学习更完整的 Makefile 时，可以使用：

```text
-MMD -MP
```

自动生成头文件依赖。

## 13.3 自动生成依赖的简单写法

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra -MMD -MP
TARGET = app
OBJS = main.o led.o
DEPS = $(OBJS:.o=.d)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $^ -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

-include $(DEPS)

clean:
	rm -f $(TARGET) $(OBJS) $(DEPS)
```

这里会自动生成：

```text
main.d
led.d
```

`.d` 文件中记录了 `.c` 文件依赖哪些头文件。

## 14 交叉编译中的 Makefile

## 14.1 修改编译器

如果要从本机编译改为 ARM64 交叉编译，可以修改：

```text
CC = aarch64-linux-gnu-gcc
```

其他规则可以基本不变。

示例：

```text
CC = aarch64-linux-gnu-gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
OBJS = main.o led.o
```

## 14.2 使用 CROSS_COMPILE

嵌入式项目和 Linux 内核中经常使用：

```text
CROSS_COMPILE = aarch64-linux-gnu-
CC = $(CROSS_COMPILE)gcc
```

这样可以统一切换工具链前缀。

示例：

```text
CROSS_COMPILE = aarch64-linux-gnu-
CC = $(CROSS_COMPILE)gcc
AR = $(CROSS_COMPILE)ar
LD = $(CROSS_COMPILE)ld
```

## 14.3 从命令行覆盖变量

Makefile 中写：

```text
CC = gcc
```

执行 make 时可以覆盖：

```bash
make CC=aarch64-linux-gnu-gcc
```

也可以覆盖编译选项：

```bash
make CFLAGS="-g -O0 -Wall -Wextra"
```

这在调试不同工具链时很有用。

## 15 常见错误

## 15.1 命令前面用了空格

错误：

```text
app: main.c
    gcc main.c -o app
```

如果命令前面是空格，可能报错：

```text
missing separator
```

正确：

```text
app: main.c
	gcc main.c -o app
```

命令前面必须是 Tab。

## 15.2 目标和依赖写反

错误：

```text
main.c: app
	gcc main.c -o app
```

正确：

```text
app: main.c
	gcc main.c -o app
```

目标是要生成的东西，依赖是生成它需要的东西。

## 15.3 忘记编译某个源文件

如果 `main.c` 调用了 `led_init()`，但没有编译 `led.c`，可能报：

```text
undefined reference to `led_init'
```

解决：

```text
OBJS = main.o led.o
```

确保 `led.o` 参与链接。

## 15.4 clean 没有声明为 .PHONY

建议写：

```text
.PHONY: clean
```

更完整：

```text
.PHONY: all clean
```

## 15.5 变量名拼错

示例：

```text
CFLAGS = -Wall
CFLAG = -O0
```

使用时：

```text
$(CC) $(CFLAGS) -c $< -o $@
```

这里 `CFLAG` 不会生效。

Makefile 对变量名拼写很敏感。

## 16 推荐模板

## 16.1 简单 C 项目模板

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra -MMD -MP
LDFLAGS =
TARGET = app
OBJS = main.o led.o
DEPS = $(OBJS:.o=.d)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $^ $(LDFLAGS) -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

-include $(DEPS)

clean:
	rm -f $(TARGET) $(OBJS) $(DEPS)
```

## 16.2 使用方法

编译：

```bash
make
```

清理：

```bash
make clean
```

指定编译器：

```bash
make CC=aarch64-linux-gnu-gcc
```

指定额外选项：

```bash
make CFLAGS="-g -O0 -Wall -Wextra"
```

## 17 简单练习

## 17.1 单文件 Makefile 练习

创建：

```text
main.c
Makefile
```

Makefile 内容：

```text
app: main.c
	gcc main.c -o app
```

执行：

```bash
make
./app
```

## 17.2 多文件 Makefile 练习

创建：

```text
main.c
led.c
led.h
Makefile
```

Makefile 内容：

```text
CC = gcc
CFLAGS = -g -O0 -Wall -Wextra
TARGET = app
OBJS = main.o led.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $^ -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJS)
```

执行：

```bash
make
make clean
```

## 17.3 观察增量编译

步骤：

1. 执行 `make`。
2. 再执行一次 `make`。
3. 修改 `led.c`。
4. 再执行 `make`。

观察哪些文件会被重新编译。

## 18 小结

Makefile 是 C 项目构建的基础工具。

需要重点记住：

1. Makefile 用来描述如何编译项目。
2. 基本规则格式是 `目标: 依赖` 加命令。
3. 命令前面必须是 Tab。
4. `make` 默认执行第一个目标。
5. `make clean` 常用于清理编译产物。
6. `.PHONY` 用于声明伪目标。
7. `CC` 表示编译器。
8. `CFLAGS` 表示编译选项。
9. `OBJS` 表示目标文件列表。
10. `$@` 表示目标。
11. `$<` 表示第一个依赖。
12. `$^` 表示全部依赖。
13. `%.o: %.c` 是常见模式规则。
14. 多文件项目通常先生成 `.o`，再链接成可执行文件。
15. 交叉编译时通常只需要切换 `CC` 或 `CROSS_COMPILE`。

掌握 Makefile 基础后，再学习 Linux 内核 Kbuild、U-Boot 构建系统和嵌入式项目构建流程会更容易。
