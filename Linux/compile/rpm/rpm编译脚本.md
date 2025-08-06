下面是你要的：一个**一键自动构建并安装内核 RPM 包的脚本**，你只需要传入一个 tag 或 commit id，它会：

1. 克隆或更新内核源码
2. 检出指定的 tag/commit
3. 自动配置内核（基于当前系统 `.config`）
4. 编译并生成 RPM
5. 自动使用 `dnf` 安装内核
6. 提示设置默认启动项或立即重启

---

## ✅ 脚本内容：`build_kernel_rpm.sh`

```bash
#!/bin/bash

set -e

# 参数校验
if [ $# -ne 1 ]; then
    echo "用法: $0 <tag 或 commit-id>"
    exit 1
fi

KERNEL_REF=$1
JOBS=$(nproc)
BUILD_DIR=~/kernel-build
#REPO_URL=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
REPO_URL=https://mirrors.tuna.tsinghua.edu.cn/git/linux.git

echo "👉 使用 tag/commit: $KERNEL_REF"
echo "👉 构建目录: $BUILD_DIR"

# 安装必要依赖
echo "✅ 安装依赖..."
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y ncurses-devel elfutils-libelf-devel openssl-devel bc flex bison rpm-build wget

# 克隆源码
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

if [ ! -d linux ]; then
    echo "⬇️ 克隆 Linux 内核源码..."
    git clone --depth=1 "$REPO_URL" linux
fi

cd linux
echo "🔁 拉取更新并检出 $KERNEL_REF ..."
git fetch --all
git checkout "$KERNEL_REF"

# 清理旧状态
make mrproper

# 拷贝当前系统配置
if [ -f /boot/config-$(uname -r) ]; then
    cp /boot/config-$(uname -r) .config
else
    echo "⚠️ 无法找到当前内核配置，默认使用 defconfig"
    make defconfig
fi

make olddefconfig

# 编译并生成 RPM 包
echo "⚙️ 开始构建 RPM 包..."
make -j"$JOBS" rpm-pkg

# 安装生成的 RPM
echo "📦 安装内核 RPM..."
RPM_DIR=~/rpmbuild/RPMS/$(uname -m)
sudo dnf install -y "$RPM_DIR"/kernel-[0-9]*.rpm

# 提示完成
echo "✅ 内核安装完成！可使用以下命令切换默认启动项："
echo
echo "  grep ^title /boot/loader/entries/*.conf"
echo "  grub2-set-default <bls-entry>"
echo "  reboot"
echo
uname -r
```

---

## ✅ 使用方法

1. 保存为 `build_kernel_rpm.sh`
2. 赋予可执行权限：

   ```bash
   chmod +x build_kernel_rpm.sh
   ```
3. 使用示例：

```bash
./build_kernel_rpm.sh v6.6
```

或：

```bash
./build_kernel_rpm.sh 2d3a2f8a59d3e7ac7bd...
```

---

## 🔐 安全说明

* 所有 sudo 操作仅用于安装依赖、安装 RPM，不会做危险写操作
* 构建目录是 `~/kernel-build` 和 `~/rpmbuild`，不会污染系统
* RPM 安装的内核可以用 `dnf remove` 卸载，自动清理启动项

---

如你想添加自动设置默认启动、构建日志、远程上传等高级功能，也可以告诉我，我可以扩展这个脚本为你定制。
