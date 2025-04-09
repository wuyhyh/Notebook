# 第6章 高级I/O函数

Linux基础I/O函数，read和write；

Linux还提供了很多高级的I/O函数，在特定条件下具有优秀的性能。

本章讨论其中的一部分，分为三类：

- 用于创建文件描述符的函数，pipe dup/dup2
- 用于读取数据的函数，readv/writev sendfile mmap munmap splice tee
- 用于控制I/O行为和特性的函数，fcntl

## 6.1 pipe 函数

pipe函数创建一个管道，实现进程间通信。

```c++
int pipe(int fd[2]);
```

## 6.2 dup函数和dup2函数

输入输出的重定向，使用dup或dup2函数实现：

```c++
int dup(int fd);
int dup2(int fd_1, int fd_2);
```

## 6.3 readv 函数和 writev 函数

readv函数将数据从文件描述符读到分散的内存块中，即分散读；

writev函数将多块分散内存中的数据一并写入文件描述符中，即集中写。

```c++
ssize_t readv(int fd, const struct iovec *vector, int count);
ssize_t writev(int fd, const struct iovec *vector, int count);
```

## 6.4 sendfile 函数

sendfile()在两个文件描述符之间直接传递数据（完全在内核中操作），避免了内核缓冲区和用户缓冲区之间的数据拷贝，zero-copy.

```c++
ssize_t sendfile(int out_fd, int in_fd, off_t *offset, size_t count);
```

## 6.5 mmap 函数和 munmap 函数

mmap()用于申请一段内存空间；
munmap()释放由mmap()创建的这段内存空间；

```c++
void *mmap(void *start, size_t length, int prot, int flags, int fd, off_t offset);
int munmap(void *start, size_t length); 
```

## 6.6 splice函数

splice()也用于两个文件描述符之间移动数据，也是zero-copy操作；

## 6.7 tee函数

tee()在两个管道文件描述符之间复制数据们也是zero-copy操作。

## 6.8 fcntl函数

fcntl()提供了对文件描述符的各种控制操作：

```c++
int fcntl(int fd, int cmd, ...);
```
