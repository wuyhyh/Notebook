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
# REPO_URL=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
REPO_URL=https://mirrors.tuna.tsinghua.edu.cn/git/linux.git

echo "👉 使用 tag/commit: $KERNEL_REF"
echo "👉 构建目录: $BUILD_DIR"

# 安装必要依赖
echo "✅ 安装依赖..."
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
