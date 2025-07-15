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

## 重构 U-Boot QSPI 驱动




