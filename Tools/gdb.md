GDB（GNU Debugger）是 Linux 下最常用的调试工具，支持 C/C++ 以及其他语言。以下是 GDB 的常用命令和技巧：

---

## **1. 启动 GDB**

| 命令                               | 说明              |
|----------------------------------|-----------------|
| `gdb <program>`                  | 调试可执行文件         |
| `gdb <program> <core>`           | 调试 core dump 文件 |
| `gdb -p <pid>`                   | 附加到正在运行的进程      |
| `gdb --args <program> arg1 arg2` | 运行带参数的程序        |
| `gdb -q <program>`               | 启动 GDB，禁止显示欢迎信息 |

---

## **2. 运行程序**

| 命令               | 说明                  |
|------------------|---------------------|
| `run` / `r`      | 运行程序                |
| `run arg1 arg2`  | 运行程序并传递参数           |
| `start`          | 运行程序并在 `main()` 处暂停 |
| `continue` / `c` | 继续执行直到下一个断点或程序结束    |
| `kill`           | 终止正在调试的程序           |
| `quit` / `q`     | 退出 GDB              |

---

## **3. 断点管理**

| 命令                          | 说明                          |
|-----------------------------|-----------------------------|
| `break <func>` / `b <func>` | 在函数 `<func>` 处设置断点          |
| `break <file>:<line>`       | 在 `<file>` 的 `<line>` 行设置断点 |
| `break *<addr>`             | 在指定的内存地址 `<addr>` 处设置断点     |
| `tbreak <func>`             | 临时断点，仅触发一次                  |
| `info breakpoints` / `i b`  | 显示所有断点                      |
| `delete <num>` / `d <num>`  | 删除指定编号的断点                   |
| `disable <num>`             | 禁用指定编号的断点                   |
| `enable <num>`              | 启用指定编号的断点                   |

---

## **4. 单步执行**

| 命令               | 说明               |
|------------------|------------------|
| `step` / `s`     | 单步执行，进入函数内部      |
| `next` / `n`     | 单步执行，不进入函数内部     |
| `finish`         | 运行到当前函数返回        |
| `until`          | 运行直到当前循环结束       |
| `advance <line>` | 运行到指定行号 `<line>` |

---

## **5. 查看变量和寄存器**

| 命令                        | 说明                                               |
|---------------------------|--------------------------------------------------|
| `print <var>` / `p <var>` | 打印变量的值                                           |
| `print /x <var>`          | 以 16 进制显示变量                                      |
| `print /d <var>`          | 以 10 进制显示变量                                      |
| `print /t <var>`          | 以 2 进制显示变量                                       |
| `ptype <var>`             | 显示变量的类型                                          |
| `set var <var>=<value>`   | 修改变量的值                                           |
| `info locals`             | 显示当前作用域的所有局部变量                                   |
| `info registers`          | 显示 CPU 寄存器的值                                     |
| `x/<nfu> <addr>`          | 查看内存，格式：`n` = 显示单元数，`f` = 格式（x/d/c/s），`u` = 单元大小 |
| `x/4xb <addr>`            | 查看 4 个字节，16 进制                                   |

示例：

```gdb
p my_var       # 打印 my_var 的值
p /x my_var    # 以十六进制显示 my_var
x/4xb 0x7fffff # 以 16 进制显示 4 个字节
```

---

## **6. 线程调试**

| 命令                         | 说明             |
|----------------------------|----------------|
| `info threads`             | 显示所有线程         |
| `thread <id>`              | 切换到指定线程        |
| `bt`                       | 查看当前线程的调用栈     |
| `set scheduler-locking on` | 只运行当前线程，其他线程暂停 |

---

## **7. 查看调用栈**

| 命令                 | 说明               |
|--------------------|------------------|
| `backtrace` / `bt` | 显示当前调用栈          |
| `backtrace full`   | 显示完整的调用栈，包括变量信息  |
| `frame <n>`        | 切换到调用栈的第 `<n>` 帧 |
| `up`               | 切换到上一层调用栈        |
| `down`             | 切换到下一层调用栈        |

---

## **8. 记录和回溯**

| 命令                 | 说明         |
|--------------------|------------|
| `record`           | 开始记录程序执行路径 |
| `record stop`      | 停止记录       |
| `reverse-continue` | 逆向执行       |
| `reverse-step`     | 逆向单步执行     |
| `reverse-next`     | 逆向执行到下一行   |

---

## **9. 观察点（监视变量变化）**

| 命令                 | 说明           |
|--------------------|--------------|
| `watch <var>`      | 监视变量变化       |
| `rwatch <var>`     | 监视变量被读取      |
| `awatch <var>`     | 监视变量被访问（读/写） |
| `info watchpoints` | 显示所有监视点      |
| `delete <num>`     | 删除指定编号的监视点   |

---

## **10. 进程和核心转储**

| 命令                   | 说明                |
|----------------------|-------------------|
| `generate-core-file` | 生成 core dump 文件   |
| `core <file>`        | 加载 core dump 进行调试 |
| `bt`                 | 查看 core dump 的调用栈 |
| `info threads`       | 查看 core dump 中的线程 |

### **启用 Core Dump**

```bash
ulimit -c unlimited  # 允许生成 core dump 文件
gdb <program> core   # 调试 core dump 文件
```

---

## **11. GDB 脚本和自动化**

| 命令                         | 说明        |
|----------------------------|-----------|
| `source <file>`            | 运行 GDB 脚本 |
| `set logging on`           | 启用日志记录    |
| `set logging file gdb.log` | 设置日志文件名   |
| `set logging off`          | 关闭日志记录    |

示例 GDB 脚本 `gdb_script.txt`：

```gdb
set pagination off
break main
run
bt
info registers
quit
```

执行：

```bash
gdb -x gdb_script.txt ./a.out
```

---

## **12. 远程调试**

### **在目标机（被调试端）上启动 gdbserver**

```bash
gdbserver :1234 ./a.out
```

### **在调试机上连接**

```bash
gdb ./a.out
target remote <target-ip>:1234
```

---

### **示例：GDB 调试 C 代码**

假设 `test.c` 代码如下：

```c
#include <stdio.h>

int main() {
    int a = 10;
    int b = 0;
    int c = a / b;  // 除零错误
    printf("c = %d\n", c);
    return 0;
}
```

#### **编译并启动 GDB**

```bash
gcc -g test.c -o test
gdb ./test
```

#### **在 GDB 中调试**

```gdb
(gdb) break main    # 设置断点
(gdb) run           # 运行程序
(gdb) print a       # 打印变量 a
(gdb) backtrace     # 查看调用栈
(gdb) continue      # 继续执行
```

---

这些是 GDB 最常用的命令，掌握这些命令可以极大提高调试效率！如果有特定需求，比如 **调试多线程、动态库、远程调试**
，可以进一步深入学习相关命令。
