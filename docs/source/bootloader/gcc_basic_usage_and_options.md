# GCC 基础使用与重要编译选项

## 1. GCC 是什么

GCC 全称是 **GNU Compiler Collection**，也就是 GNU 编译器集合。它不只是一个 C 编译器，而是一组编译器前端、后端和工具链的集合，可以支持
C、C++、Fortran、Ada 等多种语言。

在日常 Linux C/C++ 开发、嵌入式开发、内核模块开发、交叉编译中，GCC 都是非常核心的工具。

平时我们执行的：

```bash
gcc main.c -o main
```

看起来只是一个命令，但 GCC 实际上会驱动多个阶段：

1. 预处理：处理 `#include`、`#define`、条件编译等
2. 编译：把 C 源码转换成汇编代码
3. 汇编：把汇编代码转换成目标文件 `.o`
4. 链接：把多个目标文件和库链接成可执行文件

GCC 的很多选项，本质上就是在控制这些不同阶段的行为。

## 2. 一个最简单的 GCC 使用示例

假设有文件 `hello.c`：

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
gcc hello.c -o hello
```

运行：

```bash
./hello
```

输出：

```text
hello gcc
```

其中：

```bash
gcc hello.c -o hello
```

含义是：

| 部分         | 含义               |
|------------|------------------|
| `gcc`      | 调用 GCC 编译器驱动程序   |
| `hello.c`  | 输入源文件            |
| `-o hello` | 指定输出文件名为 `hello` |

如果不加 `-o hello`，默认输出文件名通常是：

```bash
a.out
```

## 3. GCC 的四个主要编译阶段

### 3.1 预处理：Preprocessing

预处理阶段主要处理：

- `#include`
- `#define`
- `#ifdef`
- `#if`
- 注释删除
- 宏展开

只执行预处理：

```bash
gcc -E hello.c -o hello.i
```

生成的 `hello.i` 是预处理后的 C 文件。

常见用途：

```bash
gcc -E main.c
```

可以用来查看：

- 头文件到底展开了什么
- 宏定义是否生效
- 条件编译是否进入了预期分支

在调试复杂宏、内核宏、驱动寄存器宏时，`-E` 很有用。

### 3.2 编译：Compilation

编译阶段把 C 代码转换成汇编代码。

只编译到汇编：

```bash
gcc -S hello.c -o hello.s
```

生成：

```text
hello.s
```

这是汇编文件。

常见用途：

- 分析编译器如何生成汇编
- 学习函数调用约定
- 查看优化前后的代码差异
- 分析内联、循环优化、寄存器分配等行为

例如：

```bash
gcc -S hello.c -o hello_O0.s -O0
gcc -S hello.c -o hello_O2.s -O2
```

可以对比 `-O0` 和 `-O2` 生成的汇编差异。

### 3.3 汇编：Assembly

汇编阶段把 `.s` 汇编文件转换成目标文件 `.o`。

```bash
gcc -c hello.s -o hello.o
```

也可以直接从 `.c` 生成 `.o`：

```bash
gcc -c hello.c -o hello.o
```

`-c` 的含义是：只编译/汇编，不进行最终链接。

目标文件 `.o` 还不能直接运行，因为它通常还没有完成符号解析和库链接。

### 3.4 链接：Linking

链接阶段把一个或多个 `.o` 文件，以及需要的库文件，合并成最终可执行文件。

```bash
gcc hello.o -o hello
```

如果有多个源文件：

```bash
gcc -c main.c -o main.o
gcc -c add.c -o add.o
gcc main.o add.o -o app
```

也可以一步完成：

```bash
gcc main.c add.c -o app
```

不过在正式工程中，通常会分开编译，再统一链接。这样可以减少重复编译，提高构建效率。

## 4. GCC 编译流程总览

可以用下面这张逻辑图理解：

```text
hello.c
  |
  |  gcc -E
  v
hello.i        预处理后的 C 文件
  |
  |  gcc -S
  v
hello.s        汇编文件
  |
  |  gcc -c
  v
hello.o        目标文件
  |
  |  gcc
  v
hello          可执行文件
```

对应命令：

```bash
gcc -E hello.c -o hello.i
gcc -S hello.i -o hello.s
gcc -c hello.s -o hello.o
gcc hello.o -o hello
```

实际开发中更常见的是：

```bash
gcc -Wall -Wextra -g -O0 hello.c -o hello
```

## 5. 常用基础选项

### 5.1 `-o`：指定输出文件名

```bash
gcc main.c -o main
```

如果不指定 `-o`，默认输出通常是 `a.out`。

### 5.2 `-c`：只编译，不链接

```bash
gcc -c main.c -o main.o
```

适合多文件工程：

```bash
gcc -c main.c -o main.o
gcc -c driver.c -o driver.o
gcc -c util.c -o util.o
gcc main.o driver.o util.o -o app
```

### 5.3 `-E`：只进行预处理

```bash
gcc -E main.c -o main.i
```

适合查看宏展开结果。

常见调试场景：

```bash
gcc -E -DDEBUG main.c
```

查看 `DEBUG` 宏打开后，源码实际变成了什么。

### 5.4 `-S`：生成汇编代码

```bash
gcc -S main.c -o main.s
```

常用于：

- 学习 C 到汇编的对应关系
- 分析优化结果
- 分析 ABI、函数调用、栈帧
- 分析内联函数是否真的内联

### 5.5 `-v`：显示详细编译过程

```bash
gcc -v main.c -o main
```

可以看到：

- GCC 版本
- 默认搜索路径
- 调用的内部工具
- 头文件搜索路径
- 库搜索路径
- 目标平台信息

在交叉编译、环境排查时非常有用。

### 5.6 `--version`：查看 GCC 版本

```bash
gcc --version
```

在内核、驱动、嵌入式开发中，GCC 版本非常重要。不同版本可能影响：

- 编译选项支持情况
- 优化行为
- 警告行为
- ABI 兼容性
- 内核是否支持该编译器版本

## 6. 语言标准相关选项

### 6.1 `-std=`

指定 C/C++ 语言标准。

常见 C 标准：

```bash
gcc -std=c89 main.c -o main
gcc -std=c99 main.c -o main
gcc -std=c11 main.c -o main
gcc -std=c17 main.c -o main
gcc -std=gnu11 main.c -o main
```

常见 C++ 标准：

```bash
g++ -std=c++11 main.cpp -o main
g++ -std=c++14 main.cpp -o main
g++ -std=c++17 main.cpp -o main
g++ -std=c++20 main.cpp -o main
```

需要注意：

| 选项           | 含义                  |
|--------------|---------------------|
| `-std=c11`   | 使用标准 C11，尽量遵循 ISO C |
| `-std=gnu11` | 使用 GNU 扩展版 C11      |
| `-std=c99`   | 使用 C99 标准           |
| `-std=gnu99` | 使用 GNU 扩展版 C99      |

在 Linux 内核和很多系统软件中，常会使用 GNU 扩展，因此 `gnu11`、`gnu99` 这类模式比较常见。

### 6.2 `gcc` 和 `g++` 的区别

编译 C 文件：

```bash
gcc main.c -o main
```

编译 C++ 文件：

```bash
g++ main.cpp -o main
```

主要区别：

| 命令    | 主要用途                            |
|-------|---------------------------------|
| `gcc` | C 编译，当然也可以驱动其他语言，但默认按 C 处理 `.c` |
| `g++` | C++ 编译，会自动链接 C++ 标准库            |

例如：

```bash
gcc main.cpp -o main
```

可能出现 C++ 标准库链接问题。

更推荐：

```bash
g++ main.cpp -o main
```

## 7. 头文件与宏相关选项

### 7.1 `-I`：指定头文件搜索路径

```bash
gcc main.c -I./include -o main
```

如果代码中有：

```c
#include "driver.h"
```

而 `driver.h` 位于：

```text
project/include/driver.h
```

则可以：

```bash
gcc src/main.c -Iinclude -o app
```

多个头文件路径：

```bash
gcc main.c -Iinclude -I../common/include -o app
```

### 7.2 `-D`：定义宏

```bash
gcc main.c -DDEBUG -o main
```

等价于在源码前面写：

```c
#define DEBUG
```

也可以定义带值的宏：

```bash
gcc main.c -DLEVEL=3 -o main
```

等价于：

```c
#define LEVEL 3
```

常见用法：

```bash
gcc main.c -DCONFIG_DEBUG -DLOG_LEVEL=2 -o main
```

在驱动、BSP、移植代码中，经常用 `-D` 控制条件编译。

### 7.3 `-U`：取消宏定义

```bash
gcc main.c -UDEBUG -o main
```

表示取消 `DEBUG` 这个宏。

### 7.4 示例：用宏控制调试输出

源码：

```c
#include <stdio.h>

int main(void)
{
#ifdef DEBUG
    printf("debug mode\n");
#endif

    printf("normal code\n");
    return 0;
}
```

普通编译：

```bash
gcc main.c -o main
```

输出：

```text
normal code
```

打开 DEBUG：

```bash
gcc main.c -DDEBUG -o main
```

输出：

```text
debug mode
normal code
```

## 8. 警告选项

警告选项非常重要。对实习生培训时，建议明确要求：

> 代码至少要在 `-Wall -Wextra` 下无明显警告。

### 8.1 `-Wall`

```bash
gcc main.c -Wall -o main
```

开启一组常用警告。

注意：`-Wall` 并不是“所有警告”，只是 GCC 认为比较常用、比较合理的一组警告。

### 8.2 `-Wextra`

```bash
gcc main.c -Wall -Wextra -o main
```

开启更多额外警告。

建议日常使用：

```bash
gcc main.c -Wall -Wextra -o main
```

### 8.3 `-Werror`

```bash
gcc main.c -Wall -Wextra -Werror -o main
```

把警告当成错误。

优点：

- 强制开发者处理警告
- 避免警告长期堆积
- 适合 CI 或正式版本构建

缺点：

- 不同 GCC 版本可能产生不同警告
- 老项目直接打开可能导致大量构建失败

建议：

- 新项目可以逐步引入
- CI 中可以打开
- 对第三方代码不要轻易全局加 `-Werror`

### 8.4 `-Wno-xxx`

关闭某个警告。

例如：

```bash
gcc main.c -Wall -Wextra -Wno-unused-parameter -o main
```

关闭未使用参数警告。

在内核或驱动代码中，有时某些函数签名必须符合框架要求，即使参数没用，也不能删掉。这时可以局部处理。

不过不建议一上来就乱加 `-Wno-*`。更好的方式是先理解警告原因，再决定是否关闭。

### 8.5 常见警告选项

| 选项                      | 含义                 |
|-------------------------|--------------------|
| `-Wall`                 | 开启常用警告             |
| `-Wextra`               | 开启额外警告             |
| `-Werror`               | 将警告视为错误            |
| `-Wno-unused-parameter` | 不警告未使用参数           |
| `-Wshadow`              | 警告变量遮蔽             |
| `-Wformat`              | 检查 printf/scanf 格式 |
| `-Wformat-security`     | 检查潜在格式化字符串安全问题     |
| `-Wmissing-prototypes`  | C 代码中检查缺失函数原型      |
| `-Wstrict-prototypes`   | 检查不严格的函数声明         |
| `-Wundef`               | 使用未定义宏时警告          |

建议 C 项目基础配置：

```bash
-Wall -Wextra -Wformat=2 -Wshadow -Wundef
```

如果是 Linux 内核风格代码，还要根据内核自身构建系统来，不要随便给内核源码全局塞选项。

## 9. 调试选项

### 9.1 `-g`

```bash
gcc main.c -g -o main
```

生成调试信息，方便 GDB 调试。

配合 GDB：

```bash
gdb ./main
```

常用 GDB 命令：

```text
break main
run
next
step
print variable
bt
continue
```

### 9.2 `-g3`

```bash
gcc main.c -g3 -o main
```

`-g3` 比 `-g` 包含更多调试信息，例如宏定义信息。

当你需要在 GDB 里查看宏相关信息时，`-g3` 更有用。

### 9.3 `-ggdb`

```bash
gcc main.c -ggdb -o main
```

生成更适合 GDB 使用的调试信息。

常见开发构建：

```bash
gcc main.c -O0 -g3 -Wall -Wextra -o main
```

### 9.4 调试时为什么通常用 `-O0`

```bash
gcc main.c -O0 -g -o main
```

`-O0` 表示关闭优化。

调试时关闭优化的原因：

- 变量更容易观察
- 代码执行顺序更接近源码
- 函数不容易被内联
- 不容易出现变量被优化掉的情况

如果使用 `-O2 -g`，虽然也能调试，但可能遇到：

```text
value optimized out
```

或者源码行和实际执行不完全对应。

### 9.5 `-Og`

```bash
gcc main.c -Og -g -o main
```

`-Og` 是 GCC 提供的偏调试友好的优化级别。它会启用一部分不太影响调试体验的优化。

建议：

| 场景     | 推荐                   |
|--------|----------------------|
| 初学者调试  | `-O0 -g`             |
| 日常开发调试 | `-Og -g`             |
| 性能测试   | `-O2` 或更高            |
| 发布版本   | `-O2` / `-Os` / 项目指定 |

## 10. 优化选项

GCC 的优化选项通常以 `-O` 开头。开启优化后，编译器会尝试改善性能或代码大小，但代价可能是编译时间增加，以及调试能力下降。

### 10.1 `-O0`

```bash
gcc main.c -O0 -g -o main
```

默认优化等级通常就是 `-O0`。

特点：

- 编译速度快
- 生成代码不优化
- 方便调试
- 可执行文件性能较差

适合：

- 学习
- 调试
- 问题复现

### 10.2 `-O1`

```bash
gcc main.c -O1 -o main
```

开启基础优化。

特点：

- 比 `-O0` 性能好
- 编译时间增加不算太多
- 优化程度保守

### 10.3 `-O2`

```bash
gcc main.c -O2 -o main
```

常用发布优化等级。

特点：

- 性能优化比较充分
- 不会像 `-O3` 那样激进
- 很多项目默认使用 `-O2`

适合：

- 正式版本
- 服务器程序
- 系统软件
- 内核/驱动项目中由构建系统控制

### 10.4 `-O3`

```bash
gcc main.c -O3 -o main
```

更激进的优化。

可能包括：

- 更 aggressive 的循环优化
- 更多内联
- 更大的代码体积
- 更长编译时间

不一定总是比 `-O2` 快。

原因：

- 代码体积变大可能导致指令缓存压力增加
- 过度内联可能适得其反
- 对嵌入式系统可能不划算

建议：

> 不要迷信 `-O3`。应该通过 benchmark 验证。

### 10.5 `-Os`

```bash
gcc main.c -Os -o main
```

优化代码大小。

适合：

- 嵌入式系统
- Bootloader
- Flash 空间紧张的场景
- 对性能要求不极端但体积敏感的程序

### 10.6 `-Ofast`

```bash
gcc main.c -Ofast -o main
```

非常激进的优化。

它可能启用不完全遵守语言标准或浮点语义的优化。

不建议普通项目默认使用。

尤其是：

- 浮点计算
- 数值算法
- 对标准兼容性敏感的代码

要谨慎使用。

### 10.7 常见优化等级总结

| 选项       | 说明            | 适合场景           |
|----------|---------------|----------------|
| `-O0`    | 不优化           | 调试、学习          |
| `-Og`    | 调试友好优化        | 日常开发调试         |
| `-O1`    | 基础优化          | 轻量优化           |
| `-O2`    | 常用发布优化        | 正式版本           |
| `-O3`    | 激进优化          | 经过性能验证的场景      |
| `-Os`    | 优化体积          | 嵌入式、Bootloader |
| `-Ofast` | 非常激进，可能改变标准语义 | 特殊性能场景         |

## 11. 链接相关选项

### 11.1 `-L`：指定库搜索路径

```bash
gcc main.c -L./lib -lmylib -o main
```

表示链接时到 `./lib` 目录查找库。

### 11.2 `-l`：指定链接库

```bash
gcc main.c -lm -o main
```

链接数学库 `libm.so` 或 `libm.a`。

注意：

```bash
-lm
```

实际查找的是：

```text
libm.so
libm.a
```

也就是说：

```bash
-lxxx
```

对应：

```text
libxxx.so
libxxx.a
```

### 11.3 链接顺序问题

这是新手很容易踩坑的地方。

错误示例：

```bash
gcc -lm main.c -o main
```

有时会失败。

更推荐：

```bash
gcc main.c -lm -o main
```

一般原则：

> 被依赖的库放在后面。

例如：

```bash
gcc main.o foo.o -lbar -o app
```

如果 `foo.o` 里面调用了 `libbar` 的函数，那么 `-lbar` 应该放在 `foo.o` 后面。

### 11.4 静态链接与动态链接

默认通常是动态链接：

```bash
gcc main.c -o main
```

静态链接：

```bash
gcc main.c -static -o main
```

动态链接优点：

- 可执行文件小
- 多个程序共享动态库
- 库升级方便

静态链接优点：

- 部署简单
- 对目标系统依赖少
- 某些救援系统、嵌入式场景有用

静态链接缺点：

- 文件大
- glibc 静态链接可能引入额外兼容问题
- 安全更新不方便

### 11.5 `-Wl,option`：传递参数给链接器

GCC 是编译驱动器，真正链接通常由 `ld` 完成。

如果要把参数传给链接器，可以用：

```bash
gcc main.c -Wl,-Map=app.map -o app
```

生成链接 map 文件：

```text
app.map
```

这个文件在嵌入式开发里很有用，可以分析：

- 每个段的地址
- 符号分布
- 代码/数据大小
- 哪些目标文件被链接进来了

多个链接器参数：

```bash
gcc main.c -Wl,-Map=app.map,--gc-sections -o app
```

## 12. 代码体积与段优化

嵌入式、Bootloader、驱动开发中，经常关心最终镜像大小。

### 12.1 `-ffunction-sections`

```bash
gcc -ffunction-sections -c main.c -o main.o
```

把每个函数放到独立 section。

### 12.2 `-fdata-sections`

```bash
gcc -fdata-sections -c main.c -o main.o
```

把每个数据对象放到独立 section。

### 12.3 `-Wl,--gc-sections`

```bash
gcc main.o -Wl,--gc-sections -o app
```

让链接器丢弃未使用的 section。

通常组合使用：

```bash
gcc -Os -ffunction-sections -fdata-sections main.c -Wl,--gc-sections -o app
```

适合：

- 嵌入式应用
- Bootloader
- 裸机程序
- 体积敏感程序

## 13. 依赖文件生成选项

在 Makefile 中，经常需要自动生成头文件依赖关系。

### 13.1 `-M`

```bash
gcc -M main.c
```

输出完整依赖，包括系统头文件。

### 13.2 `-MM`

```bash
gcc -MM main.c
```

输出依赖，但不包含系统头文件。

例如：

```text
main.o: main.c driver.h common.h
```

### 13.3 `-MD`

```bash
gcc -MD -c main.c -o main.o
```

编译的同时生成 `.d` 依赖文件。

### 13.4 `-MMD`

```bash
gcc -MMD -c main.c -o main.o
```

编译时生成依赖文件，但不包含系统头文件。

Makefile 中常用：

```makefile
CFLAGS += -MMD -MP
```

### 13.5 `-MP`

```bash
gcc -MMD -MP -c main.c -o main.o
```

给依赖中的头文件生成伪目标，避免头文件删除后 Make 报错。

推荐组合：

```bash
-MMD -MP
```

这是实际工程里非常常见的依赖生成方式。

## 14. 架构与平台相关选项

### 14.1 `-m32` / `-m64`

在 x86 平台上指定生成 32 位或 64 位程序：

```bash
gcc -m32 main.c -o main32
gcc -m64 main.c -o main64
```

需要系统安装对应的 32 位库和头文件。

### 14.2 `-march=`

指定目标 CPU 架构。

例如 x86：

```bash
gcc main.c -march=x86-64 -o main
gcc main.c -march=native -o main
```

`-march=native` 表示针对当前机器 CPU 生成代码。

优点：

- 可能获得更好性能

缺点：

- 生成的二进制可能无法在其他机器上运行

例如在你自己的机器上编译：

```bash
gcc main.c -O2 -march=native -o app
```

可能在另一台较老机器上运行失败，因为用了新指令集。

### 14.3 `-mtune=`

```bash
gcc main.c -O2 -mtune=native -o app
```

`-mtune` 主要影响调度和性能调优，但不一定改变可用指令集。

简单理解：

| 选项       | 作用               |
|----------|------------------|
| `-march` | 决定可以使用哪些指令       |
| `-mtune` | 决定针对哪类 CPU 做性能调度 |

### 14.4 ARM64 交叉编译示例

比如使用 AArch64 交叉工具链：

```bash
aarch64-linux-gnu-gcc main.c -o main
```

或者：

```bash
aarch64-linux-gnueabi-gcc main.c -o main
```

常见环境变量：

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
```

Linux 内核编译中常见：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
```

在你的工作场景里，GCC 不只是编译普通应用，还经常参与：

- U-Boot 编译
- Linux Kernel 编译
- 设备树编译流程的一部分
- out-of-tree kernel module 编译
- rootfs 里的应用程序构建
- 交叉构建 ARM64 软件

## 15. 预处理和 include 路径排查

### 15.1 查看头文件搜索路径

```bash
gcc -E -v main.c -o /dev/null
```

可以看到 GCC 实际搜索了哪些 include 路径。

这在以下场景非常重要：

- 交叉编译找错头文件
- host 头文件污染 target 编译
- sysroot 配置错误
- 同名头文件冲突
- 内核头文件和用户态头文件混用

### 15.2 `-nostdinc`

```bash
gcc -nostdinc main.c -o main
```

不使用标准系统头文件路径。

这个选项普通应用很少直接用，但在：

- Linux 内核
- 裸机程序
- Bootloader
- 特殊 freestanding 环境

中会用到。

### 15.3 `-isystem`

```bash
gcc main.c -isystem ./third_party/include -o main
```

把某个路径作为“系统头文件路径”。

特点：

- 仍然可以搜索该路径
- 对其中头文件的某些警告处理会更宽松

适合第三方库头文件。

## 16. Sysroot 相关选项

### 16.1 `--sysroot=`

交叉编译时非常重要。

```bash
aarch64-linux-gnu-gcc main.c --sysroot=/opt/rootfs -o main
```

含义是让 GCC 把 `/opt/rootfs` 当成目标系统根目录来找：

- 头文件
- 库文件
- 动态链接器
- libc 相关文件

例如：

```bash
--sysroot=/opt/openeuler-aarch64-rootfs
```

这样编译 ARM64 程序时，GCC 会使用目标 rootfs 里的头文件和库，而不是 x86 host 系统的头文件和库。

这是交叉编译中非常关键的概念。

### 16.2 sysroot 常见问题

问题 1：找不到头文件：

```text
fatal error: stdio.h: No such file or directory
```

可能原因：

- sysroot 不完整
- 没安装 libc-devel
- include 路径错误
- 工具链配置错误

问题 2：找不到库：

```text
cannot find -lc
cannot find -lm
cannot find -lpthread
```

可能原因：

- sysroot 中没有对应 `.so` 或 `.a`
- 库路径不对
- 目标架构不匹配
- 软链接缺失

问题 3：链接了 host 库。

这是最危险的一类问题。例如你想编译 ARM64 程序，却不小心链接了 x86_64 的库。

排查：

```bash
file app
file /path/to/libxxx.so
```

应该看到：

```text
ELF 64-bit LSB executable, ARM aarch64
```

而不是：

```text
ELF 64-bit LSB executable, x86-64
```

## 17. 安全与加固相关选项

安全编译选项一般用于用户态程序，不一定适合裸机、Bootloader 或内核。

常见选项：

```bash
-fstack-protector-strong
-D_FORTIFY_SOURCE=2
-fPIE
-pie
-Wl,-z,relro
-Wl,-z,now
```

示例：

```bash
gcc main.c -O2 -g \
    -Wall -Wextra \
    -fstack-protector-strong \
    -D_FORTIFY_SOURCE=2 \
    -fPIE -pie \
    -Wl,-z,relro -Wl,-z,now \
    -o main
```

简单说明：

| 选项                         | 作用                   |
|----------------------------|----------------------|
| `-fstack-protector-strong` | 增强栈溢出检测              |
| `-D_FORTIFY_SOURCE=2`      | 对部分 libc 函数做额外检查     |
| `-fPIE -pie`               | 生成位置无关可执行文件          |
| `-Wl,-z,relro`             | 增强 GOT/重定位区域保护       |
| `-Wl,-z,now`               | 程序启动时立即解析符号，配合 RELRO |

注意：

> 这些选项要结合目标平台、libc、链接器、项目类型使用。不能机械地给所有工程都加。

例如：

- Linux 用户态程序：可以考虑
- 内核模块：不要照搬
- U-Boot：不要照搬
- 裸机程序：通常不适用
- 特殊交叉编译环境：要验证工具链和 libc 支持情况

## 18. 静态分析与运行时检查

### 18.1 `-fanalyzer`

GCC 提供静态分析能力：

```bash
gcc -fanalyzer main.c -o main
```

可以发现一些潜在问题，例如：

- 空指针使用
- double free
- 内存泄漏
- use-after-free
- 未初始化路径

适合对普通 C 项目做额外检查。

但在大型项目或内核代码中，可能产生较多误报，需要筛选。

### 18.2 AddressSanitizer：`-fsanitize=address`

```bash
gcc main.c -g -O1 -fsanitize=address -o main
```

用于检查：

- 越界访问
- use-after-free
- double free
- heap buffer overflow
- stack buffer overflow

示例：

```bash
gcc test.c -g -O1 -fsanitize=address -fno-omit-frame-pointer -o test
```

运行：

```bash
./test
```

如果有内存错误，程序会输出详细报告。

### 18.3 UndefinedBehaviorSanitizer：`-fsanitize=undefined`

```bash
gcc main.c -g -O1 -fsanitize=undefined -o main
```

用于发现未定义行为，例如：

- 有符号整数溢出
- 非法移位
- 空指针解引用
- 越界
- 类型不匹配

常见组合：

```bash
gcc main.c -g -O1 \
    -fsanitize=address,undefined \
    -fno-omit-frame-pointer \
    -o main
```

注意：

> Sanitizer 主要用于测试和调试，不适合直接用于正式发布版本。

## 19. 位置无关代码：PIC/PIE

### 19.1 `-fPIC`

```bash
gcc -fPIC -c lib.c -o lib.o
```

生成位置无关代码，常用于动态库。

生成动态库：

```bash
gcc -fPIC -c lib.c -o lib.o
gcc -shared lib.o -o libdemo.so
```

### 19.2 `-shared`

```bash
gcc -shared lib.o -o libdemo.so
```

生成共享库 `.so`。

### 19.3 `-fPIE` 和 `-pie`

```bash
gcc main.c -fPIE -pie -o main
```

生成位置无关可执行文件。

主要用于增强安全性，支持 ASLR。

## 20. 符号与二进制分析相关选项

### 20.1 `-rdynamic`

```bash
gcc main.c -rdynamic -o main
```

把更多符号导出到动态符号表。

在以下场景可能有用：

- backtrace
- 插件系统
- 动态加载
- crash dump 分析

### 20.2 `-fno-omit-frame-pointer`

```bash
gcc main.c -O2 -g -fno-omit-frame-pointer -o main
```

保留帧指针。

优点：

- 更容易生成准确调用栈
- perf、gdb、sanitizer 分析更友好

缺点：

- 可能略微影响性能
- 占用一个寄存器，架构相关

调试和性能分析时经常建议打开。

### 20.3 `-save-temps`

```bash
gcc main.c -save-temps -o main
```

保留中间文件：

```text
main.i
main.s
main.o
```

适合教学和排查编译过程。

## 21. freestanding 与 hosted 环境

### 21.1 hosted environment

普通 Linux 应用属于 hosted environment。

特点：

- 有操作系统
- 有标准 C 库
- 有 `main`
- 可以使用 libc
- 程序由运行时环境加载启动

普通应用：

```bash
gcc main.c -o main
```

### 21.2 freestanding environment

内核、Bootloader、裸机程序通常属于 freestanding environment。

特点：

- 不一定有标准库
- 不一定从 `main` 开始
- 启动代码自己负责
- 链接脚本自己控制内存布局
- 可能不能使用普通 libc 函数

相关选项：

```bash
-ffreestanding
-nostdlib
-nostdinc
```

例如：

```bash
aarch64-linux-gnu-gcc \
    -ffreestanding \
    -nostdlib \
    -nostdinc \
    -c start.c -o start.o
```

这类选项在 U-Boot、内核、裸机开发中比较常见，但普通应用不要乱用。

## 22. 链接脚本相关

嵌入式开发经常需要自定义链接脚本。

```bash
gcc start.o main.o -T linker.ld -o firmware.elf
```

其中：

```bash
-T linker.ld
```

表示使用指定链接脚本。

链接脚本控制：

- 程序入口
- `.text` 放在哪里
- `.data` 放在哪里
- `.bss` 放在哪里
- 栈的位置
- 特定段的对齐
- 外设映射地址
- 镜像加载地址

对于 Linux 用户态程序，一般不需要自己写链接脚本。

对于：

- Bootloader
- 裸机程序
- 固件
- 特殊内核镜像

链接脚本非常重要。

## 23. 常见工程编译命令模板

### 23.1 学习/调试模板

```bash
gcc main.c -O0 -g3 -Wall -Wextra -o main
```

适合：

- 初学者
- 调试
- 单文件测试
- 面试题验证

### 23.2 普通开发模板

```bash
gcc main.c -Og -g3 -Wall -Wextra -Wformat=2 -o main
```

适合：

- 日常开发
- 方便调试
- 有基本警告约束

### 23.3 发布版本模板

```bash
gcc main.c -O2 -Wall -Wextra -DNDEBUG -o main
```

适合：

- 普通用户态程序发布
- 关闭 assert
- 打开常规优化

### 23.4 嵌入式体积优化模板

```bash
gcc main.c \
    -Os \
    -ffunction-sections \
    -fdata-sections \
    -Wl,--gc-sections \
    -o app
```

适合：

- 嵌入式应用
- 体积敏感程序

### 23.5 调试内存问题模板

```bash
gcc main.c \
    -O1 -g3 \
    -fsanitize=address,undefined \
    -fno-omit-frame-pointer \
    -Wall -Wextra \
    -o main
```

适合：

- 内存越界排查
- use-after-free
- 未定义行为排查

### 23.6 交叉编译 ARM64 用户态程序模板

```bash
aarch64-linux-gnu-gcc main.c \
    --sysroot=/opt/rootfs-aarch64 \
    -O2 -g \
    -I/opt/rootfs-aarch64/usr/include \
    -L/opt/rootfs-aarch64/usr/lib64 \
    -o main
```

实际工程中，`--sysroot` 配置正确后，通常不需要手动写太多 `-I` 和 `-L`，但排查问题时要知道它们的作用。

## 24. Makefile 中的 GCC 使用示例

### 24.1 简单 Makefile

```makefile
CC := gcc

CFLAGS := -Wall -Wextra -O0 -g3
LDFLAGS :=

SRCS := main.c add.c
OBJS := $(SRCS:.c=.o)

TARGET := app

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(LDFLAGS) -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
```

编译：

```bash
make
```

清理：

```bash
make clean
```

### 24.2 带自动依赖的 Makefile

```makefile
CC := gcc

CFLAGS := -Wall -Wextra -O0 -g3 -MMD -MP
LDFLAGS :=

SRCS := main.c add.c
OBJS := $(SRCS:.c=.o)
DEPS := $(OBJS:.o=.d)

TARGET := app

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(LDFLAGS) -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

-include $(DEPS)

clean:
	rm -f $(OBJS) $(DEPS) $(TARGET)
```

这里：

```text
-MMD -MP
```

用于自动生成头文件依赖。

## 25. GCC 和内核/驱动开发的关系

在 Linux 内核、驱动、U-Boot、BSP 开发中，GCC 的使用方式和普通用户态程序有明显区别。

### 25.1 不要绕过内核构建系统

编译内核模块时，不应该直接：

```bash
gcc -c my_driver.c
```

而应该使用内核 kbuild：

```bash
make -C /lib/modules/$(uname -r)/build M=$PWD modules
```

交叉编译时：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
    -C /path/to/kernel \
    M=$PWD modules
```

原因：

内核模块需要大量内核构建系统提供的选项，包括：

- 内核头文件路径
- 架构相关宏
- CONFIG 配置
- 编译器选项
- modpost
- vermagic
- 符号版本
- section 规则

直接用 GCC 编译，通常会出问题。

### 25.2 查看内核实际 GCC 命令

内核编译时可以加：

```bash
make V=1
```

例如：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- V=1 -j8
```

这样可以看到完整 GCC 命令。

这是学习内核编译选项最好的方式之一。

你可以让实习生重点观察：

- `-D__KERNEL__`
- `-I` 头文件路径
- `-include` 自动包含文件
- `-mcmodel`
- `-fno-*`
- `-W*`
- `-nostdinc`
- `-ffreestanding`
- `-fno-stack-protector`
- `-fno-pic`
- 架构相关选项

### 25.3 OOT 模块开发中的 GCC

out-of-tree 模块虽然看起来是独立工程，但本质上仍然依赖内核构建系统。

典型 Makefile：

```makefile
obj-m += hello.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

编译：

```bash
make
```

交叉编译：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- KDIR=/path/to/kernel
```

## 26. 常见错误与排查方法

### 26.1 undefined reference to xxx

错误：

```text
undefined reference to `foo'
```

含义：

编译阶段通过了，但链接阶段找不到 `foo` 的定义。

常见原因：

- 少编译了某个 `.c`
- 少链接了某个 `.o`
- 少加了某个库 `-lxxx`
- 链接顺序错误
- C/C++ 符号名修饰问题

排查：

```bash
nm file.o | grep foo
nm libxxx.a | grep foo
```

### 26.2 fatal error: xxx.h: No such file or directory

错误：

```text
fatal error: driver.h: No such file or directory
```

原因：

- 头文件路径没加
- `#include` 写错
- 文件位置不对

解决：

```bash
gcc main.c -Iinclude -o main
```

排查搜索路径：

```bash
gcc -E -v main.c -o /dev/null
```

### 26.3 cannot find -lxxx

错误：

```text
/usr/bin/ld: cannot find -lxxx
```

原因：

GCC/ld 找不到：

```text
libxxx.so
libxxx.a
```

解决：

```bash
gcc main.c -L/path/to/lib -lxxx -o main
```

确认库文件：

```bash
ls /path/to/lib/libxxx.so
ls /path/to/lib/libxxx.a
```

### 26.4 file format not recognized

可能原因：

- 把错误架构的 `.o` 或 `.a` 拿来链接
- ARM64 和 x86_64 混用了
- 文件损坏
- 误把文本文件当目标文件

排查：

```bash
file main.o
file libxxx.a
```

### 26.5 version `GLIBC_xxx' not found

错误：

```text
version `GLIBC_2.34' not found
```

原因：

编译时使用的 glibc 版本比运行环境新。

解决思路：

- 在更老的系统上编译
- 使用目标系统 sysroot
- 使用容器固定构建环境
- 避免在高版本发行版上编译后丢到低版本系统运行

## 27. 给实习生的 GCC 学习路线

### 27.1 第一阶段：会用

要求掌握：

```bash
gcc main.c -o main
gcc main.c -Wall -Wextra -g -O0 -o main
gcc -c main.c -o main.o
gcc main.o util.o -o app
```

理解：

- 源文件
- 目标文件
- 可执行文件
- 编译和链接的区别

### 27.2 第二阶段：理解编译流程

要求掌握：

```bash
gcc -E main.c -o main.i
gcc -S main.c -o main.s
gcc -c main.c -o main.o
gcc main.o -o main
```

理解：

- 预处理
- 编译
- 汇编
- 链接

### 27.3 第三阶段：会处理工程问题

要求掌握：

```bash
-I
-D
-L
-l
-Wall
-Wextra
-g
-O0
-O2
-MMD
-MP
```

能够解决：

- 找不到头文件
- 找不到库
- undefined reference
- 编译警告
- 多文件编译
- Makefile 基础问题

### 27.4 第四阶段：进入系统/嵌入式开发

要求掌握：

```bash
ARCH=arm64
CROSS_COMPILE=aarch64-linux-gnu-
--sysroot
-nostdlib
-nostdinc
-ffreestanding
-T linker.ld
-Wl,-Map=xxx.map
```

理解：

- 交叉编译
- 目标平台
- sysroot
- 链接脚本
- freestanding 环境
- 内核/Bootloader 和普通应用的区别

## 28. 推荐的默认编译选项组合

### 28.1 新手学习

```bash
gcc main.c -Wall -Wextra -O0 -g3 -o main
```

### 28.2 日常 C 项目开发

```bash
gcc main.c \
    -Wall -Wextra -Wformat=2 -Wshadow -Wundef \
    -Og -g3 \
    -o main
```

### 28.3 发布版本

```bash
gcc main.c \
    -Wall -Wextra \
    -O2 -DNDEBUG \
    -o main
```

### 28.4 嵌入式体积敏感版本

```bash
gcc main.c \
    -Os \
    -ffunction-sections \
    -fdata-sections \
    -Wl,--gc-sections \
    -o main
```

### 28.5 内存问题排查

```bash
gcc main.c \
    -O1 -g3 \
    -fsanitize=address,undefined \
    -fno-omit-frame-pointer \
    -Wall -Wextra \
    -o main
```

## 29. 培训时可以安排的练习

### 29.1 练习 1：观察 GCC 四阶段输出

让实习生执行：

```bash
gcc -E hello.c -o hello.i
gcc -S hello.c -o hello.s
gcc -c hello.c -o hello.o
gcc hello.o -o hello
```

要求说明：

- `.i` 是什么
- `.s` 是什么
- `.o` 是什么
- 可执行文件是怎么来的

### 29.2 练习 2：制造一个链接错误

`main.c`：

```c
int add(int a, int b);

int main(void)
{
    return add(1, 2);
}
```

只编译：

```bash
gcc main.c -o main
```

观察：

```text
undefined reference to `add'
```

然后补充 `add.c`：

```c
int add(int a, int b)
{
    return a + b;
}
```

重新编译：

```bash
gcc main.c add.c -o main
```

让实习生理解：

> 编译通过不等于链接通过。

### 29.3 练习 3：观察 `-O0` 和 `-O2` 汇编差异

```bash
gcc -S test.c -O0 -o test_O0.s
gcc -S test.c -O2 -o test_O2.s
```

对比：

```bash
diff -u test_O0.s test_O2.s
```

观察：

- 函数是否被内联
- 循环是否被优化
- 临时变量是否消失
- 汇编数量是否变化

### 29.4 练习 4：用 `-D` 控制条件编译

```bash
gcc main.c -o main
gcc main.c -DDEBUG -o main_debug
```

观察输出差异。

### 29.5 练习 5：用 `-I` 解决头文件路径问题

目录：

```text
project/
  include/
    add.h
  src/
    main.c
    add.c
```

编译：

```bash
gcc src/main.c src/add.c -Iinclude -o app
```

## 30. 最后总结

GCC 的学习不能只停留在：

```bash
gcc main.c -o main
```

真正需要掌握的是：

1. GCC 编译流程：预处理、编译、汇编、链接
2. 常用控制选项：`-E`、`-S`、`-c`、`-o`
3. 头文件和宏：`-I`、`-D`、`-U`
4. 警告和质量控制：`-Wall`、`-Wextra`、`-Werror`
5. 调试：`-g`、`-g3`、`-Og`、`-O0`
6. 优化：`-O0`、`-O2`、`-O3`、`-Os`
7. 链接：`-L`、`-l`、`-Wl`
8. 工程依赖：`-MMD`、`-MP`
9. 交叉编译：`ARCH`、`CROSS_COMPILE`、`--sysroot`
10. 系统开发：`-ffreestanding`、`-nostdlib`、链接脚本、kbuild

对普通应用开发来说，GCC 是编译器。

对嵌入式和 Linux 系统开发来说，GCC 是整个工具链和构建体系的一部分。真正掌握 GCC，不是记住所有选项，而是知道每个阶段发生了什么、每类问题应该从哪里排查。
