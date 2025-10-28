# 持久化操作系统到 SSD 中

## 1. 复制文件

```text
cd $images_path
tar -cJhf openeuler-image-phytium.ext4.tar.xz openeuler-image-phytium.ext4
```

```text
cp -v Image $wuyh/openeuler_images/
cp -v pd2008-devboard-dsk.dtb $wuyh/openeuler_images/
cp -v openeuler-image-phytium.ext4.tar.xz $wuyh/openeuler_images/
```

## 2. 启动 initramdisk 系统

假设你已经有一份“能稳定起”的内核 `Image` 与配套 `pd2008.dtb`

建议的安全地址（按你的板子内存可适当调整，三者别重叠）

```text
setenv kernel_addr_r    0x80200000
setenv fdt_addr_r       0x8F000000
setenv ramdisk_addr_r   0x90000000
setenv fdt_high         0xffffffffffffffff
setenv initrd_high      0xffffffffffffffff
```

```text
tftpboot $kernel_addr_r Image;tftpboot $ramdisk_addr_r rootfs.cpio.gz;setexpr rdsize $filesize;tftpboot $fdt_addr_r pd2008.dtb
```

```text
setenv bootargs 'console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/sbin/init'
booti $kernel_addr_r $ramdisk_addr_r:$rdsize $fdt_addr_r
```

启动之后需要配置 **IP**，才能使用后面的网络工具下载文件到开发板。

```text
ip a
ifconfig eth0 192.168.11.105 up
ifconfig eth1 192.168.11.106 up
```

### 2.2 CPU1 的启动

```text
setenv fdt_high
setenv initrd_high
setenv kernel_addr_r  0x88000000
setenv fdt_addr_r     0xA0000000
setenv ramdisk_addr_r 0xA8000000
```

```text
tftpboot $kernel_addr_r Image;tftpboot $ramdisk_addr_r rootfs.cpio.gz;setenv rdsize $filesize;tftpboot $fdt_addr_r pd2008.dtb;fdt addr $fdt_addr_r; fdt resize
```

```text
setenv bootargs 'console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/sbin/init'
booti $kernel_addr_r $ramdisk_addr_r:$rdsize $fdt_addr_r
```




