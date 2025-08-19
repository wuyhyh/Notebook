# 使用 make rpm-pkg 构建并安装内核 RPM 包

---

## 一、准备环境

### 安装构建依赖

```bash
sudo dnf install ncurses-devel bison flex elfutils-libelf-devel elfutils-devel openssl-devel \
  dwarves perl git gcc make bc zstd xz wget rpm-build -y
```

---

## 二、准备源码目录

你应该已经有 Linux 内核源码，比如：

```bash
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux
git checkout v6.6  # 可选，指定版本
```  

---

## 三、配置内核（可选）

你可以复制现有的 `.config`，或使用 `menuconfig` 自定义：

```bash
cp /boot/config-$(uname -r) .config
make olddefconfig
make menuconfig       # 如果你想定制一下版本后缀，可设定 CONFIG_LOCALVERSION
```

---

## 四、编译生成 RPM 包

```bash
make -j$(nproc) rpm-pkg
```

这一步会花比较久时间，最终生成的 `.rpm` 包会保存在你的 `$HOME/rpmbuild/RPMS/x86_64/` 目录下（默认构建架构）。

你可以查看：

```bash
ls /root/linux/rpmbuild/RPMS/x86_64/kernel-*.rpm
```

你可能会看到类似：

```text
kernel-6.6.0_custom-1.x86_64.rpm
kernel-devel-6.6.0_custom-1.x86_64.rpm
kernel-headers-6.6.0_custom-1.x86_64.rpm
```

---

## 五、使用 `dnf` 安装内核 RPM 包

```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/kernel-6.6.0_custom-1.x86_64.rpm
```

也可以批量安装：

```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/kernel-*.rpm
```

---

## 六、重启并选择新内核

安装完成后：

* 会自动生成 BLS 启动项 `/boot/loader/entries/*.conf`
* 自动注册到 rpm 数据库
* 无需手动修改 grub

然后：

```bash
reboot
```

启动后验证：

```bash
uname -r
```

---

## 七、卸载内核时可直接使用 dnf

```bash
sudo dnf remove kernel-6.6.0_custom-1.x86_64
```

这会：

* 自动删除 `/boot/` 下对应的 `vmlinuz`、`initramfs`、`System.map`
* 自动移除 BLS 启动项
* 更加干净、可控，适合生产部署

---

## 彻底清理 6.16 内核的方法

### 方法 1：查找并手动删除文件

```bash
# 查找所有 6.16.0+ 的相关文件（含 modules）
find /boot -name "*6.16.0*" -exec rm -v {} \;
rm -rf /lib/modules/6.16.0+
rm -rf /usr/src/kernels/6.16.0+
```

---

### 方法 2：查找残留的 6.16 包（更可靠地列出包名）

```bash
rpm -qa | grep 6.16.0
```

然后手动卸载：

```bash
dnf remove kernel-headers-0:6.16.0+-3.x86_64 \
            kernel-devel-0:6.16.0+-3.x86_64 \
            kernel-modules-0:6.16.0+-3.x86_64 \
            kernel-0:6.16.0+-3.x86_64
```

注意 `+` 仍需加引号或使用通配符避免解释错误：

```bash
dnf remove "kernel*-6.16.0+-3*"
```

---
