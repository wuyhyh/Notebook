# spi 总线读取 nor flash 芯片信息错误

```text
[3.105908] spi-nor spi0.0: unrecognized JEDEC id bytes: 19 0c c3 7f f9 0c
[3.112802] spi-nor: probe of spi0.0 failed with error -2
[3.118193] phytium-qspi 28014000.spi: Flash size is invalid.
[3.124863] phytium-qspi: probe of 28014000.spi failed with error -22
```

## 1. 原因

flash芯片**S79FS01GS**的ID没有在内核里面注册

## 2. 解决办法

在内核源码目录下

```shell
vi drivers/mtd/spi-nor/spansion.c
```

找到结构体

```c
static const struct flash_info spansion_parts[] = {};
```

加入芯片参数

```c
{ "s79fs01gs", INFO6(0x190cc3, 0x7ff90c, 512 * 1024, 256,
        SPI_NOR_DUAL_READ | SPI_NOR_QUAD_READ |
        SPI_NOR_4B_OPCODES | USE_CLSR) },

```

打上补丁后重新编译内核