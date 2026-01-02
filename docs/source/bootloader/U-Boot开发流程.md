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

## 4. 引导操作系统

加载内核和设备树到内存

```text
tftp <mem-addr-1> uImage
tftp <mem-addr-2> dtb
```

从内存中的镜像启动

```text
bootm <mem-addr-1> - <mem-addr-2>
```

`bootm` 命令会将系统的控制权移交给 Linux 内核。

当 Linux 内核掌握控制权之后，bootloader 就不复存在了，内核会要求收回那些之前被 bootloader 占用的内存和系统资源。

将控制权交回给 bootloader 的唯一办法是重启开发板 (target board)。

## appendix A 使用串口工具更新 U-Boot

当 U-Boot 没有实现网络功能时，我们可以通过串口传输新版的 U-Boot对其进行更新。

### 1. 用 Tera Term 发送 YMODEM

**MobaXterm 的串口会话没有内置 X/Y/ZMODEM 的“Transfer/传输”菜单**，所以先使用 Tera Term传输文件。

#### 1.1 设置波特率

安装并打开 Tera Term → 选 **Serial**，选择你的 COM 口，波特率和 U-Boot 一致 （如 **115200** 8N1）。

#### 1.2 等待开始传输

在 U-Boot 命令行

```
setenv loadaddr 0x90000000
loady $loadaddr
```

出现 “Ready for binary (ymodem)” 提示后停住等待。

#### 1.3 选择文件开始传输

> 传输之前要设置 Tera Term 的波特率为 115200，关闭 VPN

在 Tera Term：**File → Transfer → YMODEM → Send...**，选中 `fip-all.bin`，等进度条走完。

> `filesize` 是十六进制；擦写 Flash 前要把擦除大小按扇区（常见 64KB）对齐。



现在 `fip-all.bin` 文件已经下载到了内存地址 0x90000000 处

### 2. 切换到 MobaXterm 擦写 flash 芯片

MobaXterm 比 Tera Term 对视觉友好多了，传输完文件我们可以换回这个工具继续使用。

传完后 U-Boot 会将传输字节数写入环境变量 `filesize`（16 进制）。你可查看：

```text
echo $filesize
```

> 可选校验，记下 CRC 以便之后比对。
>
> ```text
> crc32 $loadaddr $filesize
> ```
>

write 之前先进行 erase

```text
flashe <start_addr> <end_addr>
flashw <loadaddr> <start_addr> $filesize
```

### 3. 重启验证

写完并校验通过后，下电系统，然后上电重新启动

## Appendix B U-Boot 基线版本下载

<a href="../_static/files/fip-all.bin" download="fip-all.bin" class="btn btn-primary">下载 fip-all.bin</a>
<button class="btn sha-btn" onclick="copySha(this)">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">
<rect x="9" y="9" width="13" height="13" rx="2"></rect>
<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
</svg>
<span>SHA256</span>
</button>

<script>
async function copySha(el) {
  const old = el.innerHTML;
  const txt = await fetch('../_static/files/fip-all.bin.sha256').then(r=>r.text());
  const sha = (txt.match(/[0-9a-fA-F]{64}/)||[''])[0];
  if (!sha) return;
  try {
    await navigator.clipboard.writeText(sha);
  } catch {
    const ta=document.createElement('textarea');
    ta.value=sha;document.body.appendChild(ta);ta.select();
    document.execCommand('copy');document.body.removeChild(ta);
  }
  el.innerHTML='✅ 已复制'; setTimeout(()=>{el.innerHTML=old;},1200);
}
</script>

