# vanilla Linux 内核编译安装流程（适用于 Fedora + UEFI 系统）

## 前提准备：

```bash
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl git gcc make bc zstd xz wget -y
```

---

## 1. 下载并解压 vanilla 源码

```bash
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.9.3.tar.xz
tar -xvf linux-6.9.3.tar.xz
cd linux-6.9.3
```

清华镜像源：

```shell
git clone https://mirrors.tuna.tsinghua.edu.cn/git/linux.git --depth=1
```

自定义编译出的[内核的名称](./set_kernel_name脚本.md)

在 make menuconfig 中修改前缀；
在顶层 Makefile 中修改后缀；
最后生成的内核的前缀和后缀会合并

---

## 2. 准备配置文件（保留系统功能）

```bash
cp /boot/config-$(uname -r) .config
make olddefconfig
make menuconfig     # 进入终端图形界面，启用/禁用功能（可选）
```

---

## 3. 编译内核（视 CPU 耗时 10-60 分钟）

```bash
make -j$(nproc)
```

---

## 4. 安装内核模块和内核镜像

```bash
sudo make modules_install
sudo make install
```

这一步会在 `/boot/` 下生成：

* `vmlinuz-*`（内核映像）
* `initramfs-*`（可选，需手动生成）
* `System.map-*`
* 更新 `/boot/efi/EFI/fedora/` 目录下的引导项

---

## 5. 设置下次重启进入新内核

```bash
sudo reboot
```

---

## 6. 启动后验证是否进入新内核

```bash
uname -r
# 应该输出类似 6.9.3
```

查看新启动的系统信息

```shell
fastfetch
```

---
