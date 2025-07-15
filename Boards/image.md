# 制作可烧录的镜像

## 嵌入式 Linux 启动系统四要素

```text
wuyuhang@FS:~/D2000_IMG_Output$ ll
total 228448
drwxr-xr-x  2 wuyuhang wuyuhang      4096 Jul 15 16:17 ./
drwxr-x--- 14 wuyuhang wuyuhang      4096 Jul 15 15:23 ../
-rw-r--r--  1 wuyuhang wuyuhang  23351808 Jul  4  2024 Image
-rw-r--r--  1 wuyuhang wuyuhang  28660224 Jul  7  2024 Image_ramdisk
-rw-r--r--  1 wuyuhang wuyuhang      9971 Jul  8  2024 u-boot-d2000-devboard-dsk.dtb
-rw-r--r--  1 wuyuhang wuyuhang 181883937 Jul  5  2024 ubuntu_rootfs.tar.gz
```




## 具体命令

UBOOT使能启动命令

```shell
mii write 0x7 0x1e 0xa003
mii write 0x7 0x1f 0x8007
mii write 0x7 0x1e 0xa004
mii write 0x7 0x1f 0x00b0
mii write 0x7 0x1e 0xa001
mii write 0x7 0x1f 0x0164
mii read  0x7 0x11;
```

RAMDISK启动

```shell
setenv ipaddr 192.168.11.101;setenv serverip 192.168.11.100
tftpboot 0x90100000 Image_ramdisk;tftpboot 0x90000000 u-boot-d2000-devboard-dsk.dtb
setenv bootargs console=ttyAMA1,115200 earlycon=pl011,0x28001000 rdinit=/bin/sh;booti 0x90100000 - 0x90000000
```

启动以后

```shell
/bin/sh /root/run.sh
```

分区

```shell
fdisk /dev/nvme0n1
```

格式化

```shell
mkfs.ext4 /dev/nvme0n1p1
```

配置网络IP地址

```shell
ifconfig eth0 192.168.11.101 up
```

通过tftp下载文件

```shell
tftp -g -r Image 192.168.11.100
tftp -g -r u-boot-d2000-devboard-dsk.dtb 192.168.11.100
```

网络启动

```shell
setenv ipaddr 192.168.11.101;setenv serverip 192.168.11.100
tftpboot 0x90100000 Image;tftpboot 0x90000000 u-boot-d2000-devboard-dsk.dtb
setenv bootargs console=ttyAMA1,115200  audit=0 earlycon=pl011,0x28001000 noinitrd root=/dev/nvme0n1p1 rootwait rw;
booti 0x90100000 - 0x90000000
```

自动加载

```shell
setenv ipaddr 192.168.11.101;setenv serverip 192.168.11.100
setenv bootargs console=ttyAMA1,115200  audit=0 earlycon=pl011,0x28001000 noinitrd root=/dev/nvme0n1p1 rootwait rw;
setenv bootcmd "ext4load nvme 0:1 0x90100000 Image;ext4load nvme 0:1 0x90000000 u-boot-d2000-devboard-dsk.dtb;booti 0x90100000 - 0x90000000"
saveenv
```

起启动ft2000/4

```shell
setenv ipaddr 192.168.11.101;setenv serverip 192.168.11.100
tftpboot 0x90100000 Image_ramdisk;tftpboot 0x90000000 ft2004-devboard-d4-dsk.dtb
setenv bootargs console=ttyAMA0,115200 earlycon=pl011,0x28000000 rdinit=/bin/sh;booti 0x90100000 - 0x90000000
```

```shell
setenv ipaddr 192.168.11.101;setenv serverip 192.168.11.100
tftpboot 0x90100000 Image;tftpboot 0x90000000 ft2004-devboard-d4-dsk.dtb
setenv bootargs console=ttyAMA0,115200  audit=0 earlycon=pl011,0x28000000 noinitrd root=/dev/nvme0n1p2 rootwait rw;
booti 0x90100000 - 0x90000000
```

下载文件系统

```shell
mkdir  /root/nvme
mount /dev/nvme0n1p1 /root/nvme
cd /root/nvme
ifconfig eth0 192.168.11.101
tftp -g -r ubuntu_rootfs.tar.gz 192.168.11.100
gunzip ubuntu_rootfs.tar.gz;tar -xvf ubuntu_rootfs.tar
cd ubuntu_rootfs/ ; mv * ../.
```
