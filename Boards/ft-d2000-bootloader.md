# 飞腾 D2000 Uboot

## 编译 U-Boot

1. 项目源码

uboot.tar.gz

```shell
tar zxf uboot.tar.gz
```

2. 安装交叉编译工具链

- 内核编译工具
- arm64 架构的 gcc
- 将 gcc 添加到环境变量中

3. 交叉编译

```shell
time bear -- make ARCH=arm CROSS_COMPILE=aarch64-linux-gnu- -j12
```

4. [生成的产物](./build_result.md)

## 组装可烧录的镜像

## 烧录镜像

## 定制化 U-Boot 功能

1. 观察调试信息

使用 UART 线连接对应的串口，配置波特率观察启动时输出的日志信息

使用 Ethernet 线连接网口，配置同网段的 IPv4 地址，实现文件传输和命令发送

2. 代码走读

[U-Boot 的原理](./how_uboot_works.md)


## 重构 U-Boot QSPI 驱动




