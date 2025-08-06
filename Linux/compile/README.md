# 编译 Linux 内核

## 内核源码的获取

- vanilla kernel

从 [kernel.org](https://www.kernel.org/) 下载的 Linux 主线内核源码，未经任何发行版修改

- Git

```shell
git clone https://github.com/torvalds/linux.git
```

这个文件非常大，只 clone 最新版的代码：

```bash
git clone https://github.com/torvalds/linux.git --depth=1
```

使用[清华的镜像源](https://mirrors.tuna.tsinghua.edu.cn/help/linux.git/)：

```shell
git clone https://mirrors.tuna.tsinghua.edu.cn/git/linux.git --depth=1
```

## 在 Fedora 上编译内核

- 安装工具

```bash
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl gcc make bc wget zstd xz
```

- 配置内核

最小化组件，一般用来验证编译工具链的完整性

```shell
make defconfig
```

当前硬件的实用编译配置

```shell
cp /boot/config-$(uname -r) .config
make olddefconfig      
make menuconfig
```

- 并行编译内核

```shell
make -j${nproc}
```

使用12个核心并行编译内核，记录编译时间并生成编译数据库

```shell
time bear -- make -j12
```

分步编译

```shell
make bzImage
make modules
```

- 安装内核模块

```shell
make modules_install
```

- 安装内核

```shell
make install
```

- 更新启动项 UEFI 固件

```shell
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo reboot
```

- 清理编译产物，彻底清理生成的文件

```shell
make clean
make mrproper
```

- 显示fedora的图标

```shell
dnf install fastfetch
```

- 查看可以启动的内核

```shell
cat /boot/loader/entries/
```

查看默认启动内核

```shell
grub2-editenv list
```

```text
[root@Fedora ~]# ls /boot/loader/entries/
2f88f64cb26a4c31afec27c8a0dcb800-0-rescue.conf
2f88f64cb26a4c31afec27c8a0dcb800-6.16.0+.conf
2f88f64cb26a4c31afec27c8a0dcb800-6.14.0-63.fc42.x86_64.conf
```

前面的字符串是机器 ID

```shell
cat /etc/machine-id
```
