# U-Boot 代码的结构

## U-Boot 的 coding style

[Linux 内核编码规范](https://www.kernel.org/doc/html/v4.14/translations/zh_CN/coding-style.html#kconfig)

## 源码目录

[U-Boot 社区文档](https://docs.u-boot.org/en/latest/?_gl=1*11h31yz*_ga*MTM5ODY5NzIzMC4xNzUyNTY1OTMx*_ga_XNSR1J4G4Z*czE3NTI1NjU5MzAkbzEkZzAkdDE3NTI1NjU5MzAkajYwJGwwJGgw)

[U-Boot github](https://github.com/u-boot/u-boot)

| 目录         | 说明                                      |
|------------|-----------------------------------------|
| `arch/`    | 与架构相关的代码（如 ARM、x86、RISCV 等）             |
| `board/`   | 与具体开发板相关的初始化代码                          |
| `cmd/`     | U-Boot 命令实现，如 `bootm`, `loadb`, `env` 等 |
| `common/`  | 通用逻辑，如启动流程、命令注册、控制台等                    |
| `drivers/` | 各类驱动实现（串口、网络、SPI、USB等）                  |
| `env/`     | 环境变量管理                                  |
| `fs/`      | 文件系统支持（如 FAT, EXT4）                     |
| `lib/`     | 常用库函数（zlib、crc、hash等）                   |
| `include/` | 头文件目录                                   |
| `configs/` | 各平台的 defconfig 配置文件                     |
| `tools/`   | 辅助工具构建，如 mkimage 等                      |

[编译后的源码目录解析](./build_result.md)

