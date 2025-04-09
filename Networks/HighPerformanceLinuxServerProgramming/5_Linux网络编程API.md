# 第5章 Linux网络编程API

本章从三个方面讨论网络编程API

- socket地址API，socket最开始的含义是一个IP地址和端口对，唯一地表示了使用TCP通信的一端
- socket基础API，定义在sys/socket.h中，包括创建socket，命名socket，监听socket、接受连接、发起连接、读写数据等；
- 网络信息API，实现主机名和IP地址之间的转换，服务名称和端口号之间的转换。`netdb.h`

## 5.1 socket 地址API

### 5.1.1 主机字节序和网络字节序

### 5.1.2 通用socket地址

socket网络编程接口表示socket地址的结构体`sockaddr`

### 5.1.3 专用socket地址

### 5.1.4 IP 地址转换函数

点分十进制与二进制之间的转换

## 5.2 创建 socket

socket是一个可读、可写、可控制、可关闭的文件描述符。

```c++
int socket(int domain, int type, int protocol);
```

socket系统调用成功时返回一个socket文件描述符，失败时返回-1

## 5.3 命名socket

将一个socket与socket地址绑定称为给socket命名。

```c++
int bind(int sockfd, const struct sockaddr *my_addr, socklen_t addrlen);
```

## 5.4 监听socket

socket被命名之后，还不能马上接受客户连接，我们需要使用如下的系统调用来创建一个监听队列来存放待处理的客户连接。

```c++
int listen(int sockfd,  int backlog);
```

## 5.5 接受连接

下面的系统调用从listen监听队列中接受一个连接

```c++
int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
```

## 5.6 发起连接

服务器端通过listen调用来被动接受连接；
客户端通过connect调用来主动与服务器建立连接。

```c++
int connect(int sockfd, const struct sockaddr *serv_addr, socklen_t addrlen);
```

## 5.7 关闭连接

关闭连接就是关闭对应的socket文件描述符，可以通过普通的文件描述符系统调用来关闭:

```c++
int close(int fd);
```

close系统调用并不总是关闭一个socket连接，而是将fd引用计数减1。

如果要立即终止一个连接，使用shutdown系统调用：

```c++
int shutdown(int sockfd, int howto);
```

## 5.8 数据读写

### 5.8.1 TCP 数据读写

文件的读写使用read write，同样适用于socket；
同时socket还有专门的数据读写系统调用：

```c++
ssize_t recv(int sockfd, void *buf, size_t len, int flags);
ssize_t send(int sockfd, const void *buf, size_t len, int flags);
```

### 5.8.2 UDP 数据读写

### 5.8.3 通用数据读写

## 5.9 带外标记

Linux内核检测到TCP紧急标记时，将通知应用程序有带外数据需要接收。

内核通知应用带外数据到达的两种常见方式是：I/O复用产生的异常事件和SIGURG信号。

## 5.10 地址信息函数

在某些情况下，我们需要知道一个连接socket的本端socket地址以及远端socket地址：

```c++
int getsockname(int sockfd, struct sockaddr *address, socklen_t address_len);
int getpeername(int sockfd, struct sockaddr *address, socklen_t address_len);
```

## 5.11 socket选项

fcntl系统调用控制文件描述符属性；

类似的，下面两个系统调用专门用来读取和设置socket文件描述符属性：

```c++
int getsockopt(int sockfd, int level, int option_name, void* option_value, socklen_t * restrict option_len);
int setsockopt(int sockfd, int level, int option_name, const void* option_value, socklen_t * restrict option_len);
```

## 5.12 网络信息 API

socket地址的两个要素，IP地址和端口号都是数值表示的，不便于记忆和扩展。
需要一些API实现数值和人类优化的名称的转换。

### 5.12.1 gethostbyname 和 gethostbyaddr

### 5.12.2 getservbyname 和 getservbyaddr

### 5.12.3 getaddrinfo

### 5.12.4 getnameinfo
