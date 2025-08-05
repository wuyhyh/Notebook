非常好，我们逐一解答你的问题，并在最后提供一个 **完整的 vanilla 内核编译、安装、启动流程（UEFI 专用）**。

---

## ✅ 问题 1：在执行 `make menuconfig` 之前需要准备 `.config` 文件吗？

取决于你是否希望**复用当前系统的配置**：

### ✅ 推荐操作：

```bash
cp /boot/config-$(uname -r) .config
make olddefconfig     # 补齐新内核中新增的配置项
make menuconfig       # 此时进去就是完整的、系统当前的配置基础
```

### 📌 为什么不直接 `make menuconfig`？

如果你不手动准备 `.config` 文件，那么：

* 会使用默认的 `defconfig`（通常是针对某些架构的最小功能集）
* 很多你当前系统需要的驱动和模块不会启用
* 编译出的内核可能无法驱动你的网络、显卡等

### 总结：

| 操作                                              | 是否建议  | 原因          |
|-------------------------------------------------|-------|-------------|
| 直接 `make menuconfig`                            | ❌ 不建议 | 缺少当前系统配置基础  |
| 先 `cp config && make olddefconfig` 再 menuconfig | ✅ 推荐  | 保留现有功能并可自定义 |

---

## ✅ 问题 2：UEFI 系统中 grub 配置和默认项设置命令

Fedora UEFI 系统的 grub 配置文件在：

```
/boot/efi/EFI/fedora/grub.cfg
```

但这是由 `/etc/grub2-efi.cfg` 链接生成的，一般我们使用如下命令管理 grub：

### 🧭 1. 生成 grub 配置文件

```bash
sudo grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
```

或者（两者等价）：

```bash
sudo grub2-mkconfig -o /etc/grub2-efi.cfg
```

### 🔁 2. 设置下次重启临时使用某个内核（索引从 0 开始）

```bash
sudo grub2-reboot 1
sudo reboot
```

### 🖥️ 3. 设置默认启动项

```bash
sudo grub2-set-default 1
```

### 👀 4. 查看当前启动项索引和列表

```bash
awk -F\' '$1=="menuentry " {print i++ " : " $2}' /boot/efi/EFI/fedora/grub.cfg
```

---

## ✅ 完整：vanilla Linux 内核编译安装流程（适用于 Fedora + UEFI 系统）

### 🍰 前提准备：

```bash
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel openssl-devel \
  dwarves perl gcc make bc zstd xz wget
```

---

### 📥 1. 下载并解压 vanilla 源码

```bash
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.9.3.tar.xz
tar -xvf linux-6.9.3.tar.xz
cd linux-6.9.3
```

---

### ⚙️ 2. 准备配置文件（保留系统功能）

```bash
cp /boot/config-$(uname -r) .config
make olddefconfig
make menuconfig     # 进入终端图形界面，启用/禁用功能（可选）
```

---

### 🧱 3. 编译内核（视 CPU 耗时 10-60 分钟）

```bash
make -j$(nproc)
```

---

### 📦 4. 安装内核模块和内核镜像

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

### 🌀 5. 生成 initramfs（有时 `make install` 不自动生成）

```bash
sudo dracut --kver 6.9.3 --force
```

---

### 📑 6. 生成 grub 配置（Fedora UEFI 系统）

```bash
sudo grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
```

---

### 🔁 7. 设置下次重启进入新内核

```bash
# 查看新内核在grub中是第几个
awk -F\' '$1=="menuentry " {print i++ " : " $2}' /boot/efi/EFI/fedora/grub.cfg

# 假设新内核是第 0 项
sudo grub2-reboot 0
sudo reboot
```

---

### ✅ 8. 启动后验证是否进入新内核

```bash
uname -r
# 应该输出类似 6.9.3
```

---

### 🧹 9. 如果启动没问题，可删除旧内核（可选）

```bash
sudo dnf remove kernel-core-6.x.x
```

---

如果你希望进一步将这个流程脚本化（适合多次内核迭代开发），我可以再帮你生成一个 `build_kernel.sh` 脚本来自动化整个过程。需要吗？
