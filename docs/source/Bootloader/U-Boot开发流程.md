# U-Boot 开发流程

介绍 U-Boot 开发用到的 IDE 和需要安装的工具链

## 1. U-Boot 编译

### 1.1 安装交叉编译工具链

在 x86_64 Windows 11 的 PC 上安装 wsl, 使用的操作系统是 Ubuntu 24.04 LTS

gcc 下载自开源项目，将下载到的压缩包解压到**根目录**`~`

```text
tar -xf gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu.tar.xz
```

### 1.2 编译 bootloader

从服务器 clone 代码，IP 可能改变，在这之前你还需要配置好 SSH 访问

```text
git clone ssh://git@172.16.21.37:2222/srv/git/ft-d2000_u-boot-v1.37.git
cd ft-d2000_u-boot-v1.37
```

生成配置文件

```text
make hpc_board_defconfig
```

> 构建的时候需要交叉编译工具链，为了简化命令，实现了一个 `build.sh`
> ```bash
> export ARCH=arm
> export CROSS_COMPILE=~/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-
> 
> time bear -- make -j$(nproc)
>```

编译 bootloader

```text
./build.sh
```

> 使用 `bear` 工具的目的是生成 `compile_commands.json`，这样在 CLion 中以编译数据库项目打开可以实现方便的代码索引

### 1.3 打包工具的使用

将打包工具解压到**根目录**`~`

```text
tar -xf image_fix_d2000_v1.71.baseline.tar.xz
```

将编译出的 bootloader 文件放入 **raw_materials 目录**

```text
cp ../ft-d2000_u-boot-v1.37/u-boot.bin raw_materials/
```

打包

```text
./my_scripts/image-fix.sh
```

增加一个方便的**环境变量**

```text
echo 'export wuyh="/mnt/c/Users/wuyuhang"' >> .bashrc
```

得到的可烧录文件放置到需要的 Windows 目录下

```text
cp fip-all.bin $wuyh/Downloads
```

## 2. 使用网络更新 U-Boot 版本

### 2.1 配置网络使用 tftp 下载要写入 flash 的 bootloader

#### a. 打印环境变量

```bash
pri
```

#### b. 配置基础网络参数

```bash
setenv ipaddr 192.168.11.102
setenv serverip 192.168.11.100
saveenv
```

* **`setenv ipaddr`**：设置本机（开发板）IP 地址。
* **`setenv serverip`**：设置 TFTP 服务器 IP（U‑Boot 的 `tftpboot` 会用到）。
* **`saveenv`**：把当前环境变量持久化到环境介质（掉电不丢）。

### 2.2 使用 tftp 下载文件

在 MaboXterm 中打开 tftp server,选择存放 `fip-all.bin` 的目录，比如 `~/Downloads`

```text
tftpboot 0x90000000 fip-all.bin
```

### 2.3 在串口中擦写 flash

擦除 flash 芯片的部分区域

```text
flashe 0x0 0x500000
```

写入 flash

```text
flashw 0x90000000 0x0 $filesize
```

### 2.4 重启

写入完毕后，下电，然后上电重启系统

## 3. U-Boot 网络

配置完网络参数后，打印环境变量可以看到两个网络接口 `ethernet0@2820c000` `ethernet1@28210000`

这个环境变量避免网口的**自动切换**

```text
setenv ethrotate no
saveenv
```

指定采用 **eth0**

```text
setenv ethact ethernet0@2820c000
```

指定采用 **eth1**

```text
setenv ethact ethernet1@28210000
```

使用 **Ping** 命令验证网络，**alive** 说明网络正常

```text
D2000#ping 192.168.11.100
genphy_update_link : MII_BMSR = 69!
genphy_update_link : MII_BMSR2 = 6d!
genphy_update_link : phydev->link = 1!
Speed: 1000, full duplex
Using ethernet0@2820c000 device
host 192.168.11.100 is alive
D2000#setenv ethact ethernet1@28210000
D2000#ping 192.168.11.100
genphy_update_link : MII_BMSR = 69!
genphy_update_link : MII_BMSR2 = 6d!
genphy_update_link : phydev->link = 1!
Speed: 1000, full duplex
Using ethernet1@28210000 device
host 192.168.11.100 is alive
```
