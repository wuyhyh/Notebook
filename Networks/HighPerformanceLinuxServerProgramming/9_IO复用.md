# 第9章 I/O 复用

I/O 复用使得程序能同时监听多个文件描述符。

Linux 下实现I/O复用的系统调用主要有 select poll epoll

## 9.1 select 系统调用

select系统调用用途是：在一段指定的时间内，监听用户感兴趣的文件描述符上的可读、可写、和异常事件；

## 9.2 poll 系统调用

poll系统调用和select类似，也是在指定时间内轮询一定数量的文件描述符，以测试其中是否有就绪者。

## 9.3 epoll 系统调用

### 9.3.1 内核事件表

epoll是Linux特有的I/O复用函数。
epoll使用一组函数来完成任务，而不是单个函数。
epoll把用户关心的文件描述符上的事件放在内核的一个事件表中。

```c++
int epoll_create(int size);
```

### 9.3.2 epoll_wait函数

epoll系列系统调用的主要接口是epoll_wait()，它在一段时间内等待一组文件描述符上的事件。

### 9.3.3 LT和ET模式

epoll对文件描述符的操作有两种模式：LT和ET
