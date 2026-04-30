# 02-GCC基本使用与编译流程

## 1 文档目标

本文用于帮助实习生掌握 GCC 的基本使用方法，并理解 C 程序从源码到可执行文件的大致流程。

学习完本文后，应能够：

1. 使用 `gcc` 编译简单 C 程序。
2. 理解预处理、编译、汇编、链接四个阶段。
3. 看懂常见 GCC 选项。
4. 编译多个 `.c` 文件组成的小项目。
5. 初步理解头文件、库文件和链接错误的关系。

## 2 GCC 是什么

## 2.1 基本概念

GCC 是常用的 C/C++ 编译工具集合。

在 C 语言开发中，通常使用 `gcc` 命令把 `.c` 源文件编译成可执行程序。

示例：

```bash
gcc hello.c -o hello
```

含义：

1. `hello.c` 是输入的 C 源文件。
2. `-o hello` 指定输出文件名为 `hello`。
3. 如果没有错误，会生成可执行文件 `hello`。

运行：

```bash
./hello
```

## 2.2 一个最简单的 C 程序

```c
#include <stdio.h>

int main(void)
{
    printf("hello gcc\n");
    return 0;
}
```

保存为：

```text
hello.c
```

编译：

```bash
gcc hello.c -o hello
```

运行：

```bash
./hello
```

## 3 编译的四个阶段

C 程序从源码到可执行文件，通常经历四个阶段：

1. 预处理。
2. 编译。
3. 汇编。
4. 链接。

完整命令：

```bash
gcc hello.c -o hello
```

实际上 GCC 会在内部自动完成这几个阶段。

## 3.1 预处理

预处理主要处理：

1. `#include`
2. `#define`
3. 条件编译
4. 注释删除

只执行预处理：

```bash
gcc -E hello.c -o hello.i
```

输出文件：

```text
hello.i
```

`hello.i` 是预处理后的 C 源文件。

可以用来观察头文件展开、宏替换之后的结果。

## 3.2 编译

编译阶段把预处理后的 C 代码转换成汇编代码。

只执行到编译阶段：

```bash
gcc -S hello.c -o hello.s
```

输出文件：

```text
hello.s
```

`hello.s` 是汇编代码。

一般初学阶段不需要深入理解汇编，但需要知道这个阶段存在。

## 3.3 汇编

汇编阶段把汇编代码转换成目标文件。

只生成目标文件：

```bash
gcc -c hello.c -o hello.o
```

输出文件：

```text
hello.o
```

`hello.o` 是目标文件，还不能直接运行。

它里面包含机器代码，但还没有完成链接。

## 3.4 链接

链接阶段把一个或多个目标文件，以及需要的库文件组合成最终可执行文件。

示例：

```bash
gcc hello.o -o hello
```

输出：

```text
hello
```

此时 `hello` 才是可以运行的可执行文件。

## 4 常用 GCC 选项

## 4.1 指定输出文件 -o

```bash
gcc hello.c -o hello
```

如果不加 `-o`，默认输出文件名通常是：

```text
a.out
```

不推荐依赖默认输出名。

## 4.2 只编译不链接 -c

```bash
gcc -c hello.c -o hello.o
```

用于生成目标文件。

多文件项目中经常先把每个 `.c` 文件编译成 `.o`，最后再链接。

## 4.3 指定头文件路径 -I

如果头文件不在当前目录或系统默认目录，需要使用 `-I` 指定头文件搜索路径。

示例目录：

```text
project/
├── include/
│   └── led.h
└── src/
    └── main.c
```

编译：

```bash
gcc -Iinclude src/main.c -o app
```

含义：

```text
-Iinclude
```

告诉 GCC 去 `include` 目录中查找头文件。

## 4.4 指定库文件路径 -L

如果库文件不在系统默认路径，需要使用 `-L` 指定库文件目录。

```bash
gcc main.o -L./lib -lmylib -o app
```

含义：

1. `-L./lib`：到 `./lib` 目录查找库。
2. `-lmylib`：链接 `libmylib.so` 或 `libmylib.a`。

## 4.5 指定链接库 -l

```bash
gcc main.c -lm -o app
```

`-lm` 表示链接数学库 `libm`。

例如使用 `sqrt()` 时，可能需要：

```bash
gcc main.c -lm -o app
```

注意：库选项通常放在源文件或目标文件后面。

## 4.6 打开警告 -Wall

推荐编译时打开常用警告：

```bash
gcc -Wall hello.c -o hello
```

`-Wall` 会打开一组常见警告。

警告不是错误，但很多警告都值得修复。

## 4.7 打开更多警告 -Wextra

```bash
gcc -Wall -Wextra hello.c -o hello
```

`-Wextra` 会打开更多额外警告。

实习生练习代码时，建议默认使用：

```bash
gcc -Wall -Wextra hello.c -o hello
```

## 4.8 把警告当作错误 -Werror

```bash
gcc -Wall -Wextra -Werror hello.c -o hello
```

`-Werror` 会把警告当作错误处理。

在正式项目中很有用，但初学阶段可以先不用，避免被大量警告卡住。

## 4.9 生成调试信息 -g

```bash
gcc -g hello.c -o hello
```

`-g` 会在程序中加入调试信息，方便使用 `gdb` 调试。

开发阶段建议加上：

```bash
gcc -g -Wall -Wextra hello.c -o hello
```

## 4.10 优化选项 -O

常见优化等级：

```bash
-O0
-O1
-O2
-O3
-Os
```

含义：

1. `-O0`：不优化，适合调试。
2. `-O1`：基础优化。
3. `-O2`：常用优化等级。
4. `-O3`：更激进优化，不一定总是更好。
5. `-Os`：优化代码大小。

开发调试阶段常用：

```bash
gcc -O0 -g hello.c -o hello
```

发布或性能测试时常用：

```bash
gcc -O2 hello.c -o hello
```

## 5 多文件编译

## 5.1 示例项目结构

```text
project/
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

## 5.2 一条命令直接编译

```bash
gcc main.c led.c -o app
```

这种方式简单，适合小程序。

## 5.3 分步编译

先编译成目标文件：

```bash
gcc -c main.c -o main.o
gcc -c led.c -o led.o
```

再链接：

```bash
gcc main.o led.o -o app
```

这种方式更接近真实项目的构建流程。

## 5.4 为什么要分步编译

分步编译的好处：

1. 某个 `.c` 文件没改，就不需要重新编译它。
2. 大项目编译速度更快。
3. 更容易配合 Makefile。
4. 更清楚地区分编译错误和链接错误。

## 6 头文件和编译

## 6.1 include 的作用

```c
#include "led.h"
```

这行代码表示把 `led.h` 的内容包含进当前 `.c` 文件。

头文件通常放：

1. 宏定义。
2. 结构体定义。
3. 函数声明。
4. `extern` 变量声明。

## 6.2 头文件不等于源文件

包含头文件并不会自动编译对应的 `.c` 文件。

例如 `main.c` 中包含了：

```c
#include "led.h"
```

仍然需要编译 `led.c`：

```bash
gcc main.c led.c -o app
```

如果只编译：

```bash
gcc main.c -o app
```

可能会出现链接错误：

```text
undefined reference to `led_init'
```

原因是编译器知道 `led_init()` 的声明，但链接器找不到它的实现。

## 6.3 头文件路径错误

如果报错：

```text
fatal error: led.h: No such file or directory
```

说明 GCC 找不到头文件。

解决方法：

1. 检查头文件路径。
2. 检查 `#include` 写法。
3. 使用 `-I` 指定头文件目录。

示例：

```bash
gcc -Iinclude src/main.c src/led.c -o app
```

## 7 常见错误类型

## 7.1 语法错误

示例：

```c
int main(void)
{
    return 0
}
```

少了分号。

可能报错：

```text
error: expected ';' before '}'
```

这类错误发生在编译阶段。

## 7.2 头文件找不到

报错：

```text
fatal error: xxx.h: No such file or directory
```

常见原因：

1. 头文件路径不对。
2. 没有使用 `-I`。
3. 文件名大小写写错。

## 7.3 未定义引用

报错：

```text
undefined reference to `xxx'
```

常见原因：

1. 只写了函数声明，没有函数实现。
2. 有实现，但对应 `.c` 文件没有参与编译。
3. 链接库漏了。
4. 库顺序不对。

这是链接阶段错误。

## 7.4 重复定义

报错：

```text
multiple definition of `xxx'
```

常见原因：

1. 在头文件中定义了普通全局变量。
2. 同一个函数在多个 `.c` 文件中都定义了一遍。
3. `.c` 文件被错误地 `#include` 到另一个 `.c` 文件中。

建议：

1. 头文件放声明。
2. 源文件放定义。
3. 不要 `#include` `.c` 文件。

## 7.5 隐式函数声明

报错或警告：

```text
implicit declaration of function `xxx'
```

说明调用函数前，编译器没有看到函数声明。

解决方法：

1. 添加正确的函数声明。
2. 包含正确的头文件。
3. 检查函数名是否拼错。

## 8 查看中间结果

## 8.1 查看预处理结果

```bash
gcc -E main.c -o main.i
```

可以用来检查：

1. 宏是否正确展开。
2. 头文件是否被包含。
3. 条件编译是否生效。

## 8.2 查看汇编结果

```bash
gcc -S main.c -o main.s
```

可以看到编译器生成的汇编代码。

初学阶段只需要知道它存在，后面做底层优化、驱动调试时可能会用到。

## 8.3 查看目标文件符号

可以使用 `nm` 查看目标文件符号：

```bash
nm main.o
nm led.o
```

如果 `main.o` 中引用了 `led_init`，但 `led.o` 中没有提供，就会导致链接失败。

常见符号含义：

1. `T`：当前目标文件中定义的函数。
2. `U`：当前目标文件中引用但未定义的符号。
3. `D`：已初始化的全局变量。
4. `B`：未初始化的全局变量。

## 9 交叉编译基础

## 9.1 什么是交叉编译

交叉编译是指在一种平台上编译另一种平台运行的程序。

例如：

1. 在 x86 主机上编译 ARM64 程序。
2. 在 PC 上编译嵌入式开发板程序。

普通本机编译：

```bash
gcc main.c -o app
```

ARM64 交叉编译可能是：

```bash
aarch64-linux-gnu-gcc main.c -o app
```

具体命令取决于工具链名称。

## 9.2 查看编译器目标平台

```bash
gcc -dumpmachine
```

示例输出：

```text
x86_64-linux-gnu
```

交叉编译器：

```bash
aarch64-linux-gnu-gcc -dumpmachine
```

可能输出：

```text
aarch64-linux-gnu
```

## 9.3 交叉编译常见问题

常见问题：

1. 工具链没有安装。
2. 头文件和库文件不是目标平台的。
3. 编译出来的程序不能在当前主机运行。
4. 运行时报 `Exec format error`。

如果在 x86 主机上运行 ARM64 程序，可能会看到：

```text
cannot execute binary file: Exec format error
```

这通常表示程序架构和当前机器架构不一致。

## 10 推荐的日常编译命令

## 10.1 单文件练习

```bash
gcc -g -O0 -Wall -Wextra hello.c -o hello
```

适合学习和调试。

## 10.2 多文件练习

```bash
gcc -g -O0 -Wall -Wextra main.c led.c -o app
```

## 10.3 分步编译

```bash
gcc -g -O0 -Wall -Wextra -c main.c -o main.o
gcc -g -O0 -Wall -Wextra -c led.c -o led.o
gcc main.o led.o -o app
```

## 10.4 指定头文件目录

```bash
gcc -g -O0 -Wall -Wextra -Iinclude src/main.c src/led.c -o app
```

## 11 简单练习

## 11.1 单文件编译练习

创建 `hello.c`：

```c
#include <stdio.h>

int main(void)
{
    printf("hello gcc\n");
    return 0;
}
```

编译：

```bash
gcc -g -O0 -Wall -Wextra hello.c -o hello
```

运行：

```bash
./hello
```

## 11.2 查看编译阶段

生成预处理文件：

```bash
gcc -E hello.c -o hello.i
```

生成汇编文件：

```bash
gcc -S hello.c -o hello.s
```

生成目标文件：

```bash
gcc -c hello.c -o hello.o
```

链接：

```bash
gcc hello.o -o hello
```

观察每一步生成的文件。

## 11.3 多文件编译练习

创建三个文件：

```text
main.c
led.c
led.h
```

然后使用：

```bash
gcc -g -O0 -Wall -Wextra main.c led.c -o app
```

再尝试只编译：

```bash
gcc -g -O0 -Wall -Wextra main.c -o app
```

观察是否出现：

```text
undefined reference
```

理解头文件声明和源文件实现之间的区别。

## 12 小结

GCC 是 C 语言开发中最常用的编译工具之一。

需要重点记住：

1. `gcc hello.c -o hello` 可以把 C 文件编译成可执行文件。
2. 编译流程包括预处理、编译、汇编、链接。
3. `-E` 只做预处理。
4. `-S` 生成汇编文件。
5. `-c` 生成目标文件，不链接。
6. `-o` 指定输出文件名。
7. `-I` 指定头文件路径。
8. `-L` 指定库文件路径。
9. `-l` 指定要链接的库。
10. `-Wall -Wextra` 用于打开常见警告。
11. `-g` 用于生成调试信息。
12. `-O0` 适合调试，`-O2` 适合常规优化。
13. 头文件提供声明，源文件提供实现。
14. `undefined reference` 通常是链接阶段找不到实现。
15. 交叉编译时，要注意编译器、头文件、库文件和运行平台是否匹配。

掌握 GCC 基本使用后，再学习 Makefile、交叉编译、内核模块编译会更容易。
