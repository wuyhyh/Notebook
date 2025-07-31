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

定义与缩写
> PBF: Phytium Base Firmware
>
>UFEI: Unified Extensible Firmware Interface
>
> U-boot: Universal Boot Loader

输出文件： `u-boot.bin` 为 `PBF` 包中使用文件

## 组装可烧录的镜像

## 烧录镜像

## 定制化 U-Boot 功能

1. 观察调试信息

使用 UART 线连接对应的串口，配置波特率观察启动时输出的日志信息

使用 Ethernet 线连接网口，配置同网段的 IPv4 地址，实现文件传输和命令发送

2. 代码走读

[U-Boot 的原理](./how_uboot_works.md)

## 重构 U-Boot QSPI 驱动

mii write 0x7 0x1e 0xa003//选择page3
mii write 0x7 0x1f 0x8007//写入的值

mii write 0x7 0x1e 0xa004
mii write 0x7 0x1f 0x00b0//时钟或偏斜补偿

mii write 0x7 0x1e 0xa001
mii write 0x7 0x1f 0x0164//光模块控制

mii read 0x7 0x11;//page1，register11，reserved

软件复位
mii write 0x7 0x1e 0x0000
mii write 0x7 0x00 0x8000

mii write 0x7 0x04 0x01E1
mii write 0x7 0x09 0x0300 # 默认值：启用1000Mbps全双工协商
mii write 0x7 0x10 0x0000 # 恢复默认PHY配置

# 读取状态寄存器（Page 0, Register 1）

mii read 0x7 0x01

# 读取自动协商结果（Page 0, Register 5）

mii read 0x7 0x05



> line

```shell
mii write 0x00 0x1e 0xa003
mii write 0x00 0x1f 0x8007
```

```shell
mii write 0x00 0x1e 0xa004
mii write 0x00 0x1f 0x00b0
```

```shell
mii write 0x00 0x1e 0xa001
mii write 0x00 0x1f 0x0164
```

mii read 0x00 0x11;//page1，register11，reserved

软件复位

```shell
mii write 0x00 0x1e 0x0000
mii write 0x00 0x00 0x8000
```

```shell
mii write 0x00 0x04 0x01E1
mii write 0x00 0x09 0x0300
mii write 0x00 0x10 0x0000
```

# 读取状态寄存器（Page 0, Register 1）

mii read 0x00 0x01

# 读取自动协商结果（Page 0, Register 5）

mii read 0x00 0x05

# === 启用 RX/TX delay ===

mii write 0x00 0x1e 0xa001
mii write 0x00 0x1f 0x0164

# === 设置 1000M 全双工能力（自动协商）===

mii write 0x00 0x09 0x0200 # 广告 1000M full
mii write 0x00 0x04 0x01e0 # 广告 100/10M full
mii write 0x00 0x00 0x1340 # 启动 auto-negotiation + 重启协商

# === 可选：读取链路状态 ===

mii read 0x00 0x01 # 标准状态
mii read 0x00 0x11 # Marvell PHY status（带速度和双工信息）

- === 启用 RX/TX delay ===

```shell
mii write 0x00 0x1e 0xa001
mii write 0x00 0x1f 0x0164
```

- === 设置 1000M 全双工能力（自动协商）===

```shell
mii write 0x00 0x09 0x0200
mii write 0x00 0x00 0x1340
```

- === 可选：读取链路状态 ===

```shell
mii read 0x00 0x11
```

- 复位
  mii write 0x00 0x00 0x8000

- 读取寄存器复位是否完成
  mii read 0x00 0x00
  循环读取直到 bit 15 == 0。

mii write 0x00 0x00 0x1200 # 半双工，10Mbps，启用自动协商，loopback disable
mii write 0x00 0x00 0x1300 # 全双工，10Mbps，启用自动协商，loopback disable

mii write 0x00 0x1e 0x0000


mii write 0x00 0x1e 0x0000
mii write 0x00 0x00 0x8000
mii write 0x00 0x00 0x1300
mii read 0x00 0x11




mii write 0x7 0 0x8000      # 软复位
mii write 0x7 9 0x0E00      # 使能1000M全双工
mii write 0x7 0 0x1200      # 启动自协商
mii read 0x7 0x01              # 查看链路状态

# 1. 设置广告能力（Reg 4）：1000M全双工
=> mii write 0x00 0x04 0x01E1

# 2. 启用自动协商并触发软复位（Reg 0）
=> mii write 0x00 0x00 0x9140  # Bit 15=1 (复位) + Bit 12=1 (自动协商)

# 3. 等待链路建立（检查状态寄存器 Reg 1 的 Bit 2）
=> mii read 0x00 0x01
# 输出应为 0x796D（Bit 2=1 表示链路正常）

mii read 0x07 0x14
mii read 0x07 0x1B
