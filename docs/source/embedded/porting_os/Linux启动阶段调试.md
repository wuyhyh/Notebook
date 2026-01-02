# Linux 启动阶段调试

## 1. spi 总线读取 nor flash 芯片信息错误

### 1.1 报错信息

```text
[3.105908] spi-nor spi0.0: unrecognized JEDEC id bytes: 19 0c c3 7f f9 0c
[3.112802] spi-nor: probe of spi0.0 failed with error -2
[3.118193] phytium-qspi 28014000.spi: Flash size is invalid.
[3.124863] phytium-qspi: probe of 28014000.spi failed with error -22
```

### 1.2 原因

flash 芯片 **S79FS01GS** 的 ID 没有在内核里面注册

### 1.3 解决办法

在内核源码目录下

```shell
vim drivers/mtd/spi-nor/spansion.c
```

找到结构体

```c++
static const struct flash_info spansion_parts[] = {};
```

加入芯片参数

```c++
{ "s79fs01gs", INFO6(0x190cc3, 0x7ff90c, 512 * 1024, 256,
        SPI_NOR_DUAL_READ | SPI_NOR_QUAD_READ |
        SPI_NOR_4B_OPCODES | USE_CLSR) },

```

打上补丁后重新编译内核

## 2. 内核配置关闭 sound 卡支持

```text
[    3.085344] ALSA device list:
[    3.088315]   No soundcards found.
[    3.091906] uart-pl011 28001000.uart: no DMA platform data
[    3.112660] EXT4-fs (nvme0n1p1): recovery complete
```

## 3. 内核配置打开 infiniband 支持

## 4. RTC 系统时间获取问题

目前是手动设置
打算临时采用从宿主机利用网络获取

## 5. 清除 APM 模块

修改构建 conf 配置

## 6. 网口配置为 static

## 7. can 总线时钟修复

## 8. 修改设备树，解决早期初始化端口 early console 读取问题

## 9. 关闭 sshd

## 10. 关闭 audit

