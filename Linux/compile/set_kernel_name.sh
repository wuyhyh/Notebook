#!/bin/bash

# ====================================
# 一键设置内核名称前缀/后缀（可缺省）
# 示例:
#   ./set_kernel_name.sh           # 不修改任何版本字段，仅回显版本
#   ./set_kernel_name.sh -debug    # 仅设置后缀
#   ./set_kernel_name.sh -dbg -my  # 设置后缀和前缀
# ====================================

LOCALVERSION="$1"
EXTRAVERSION="$2"

# 检查是否在内核源码目录中
if [ ! -f Makefile ] || [ ! -f Kconfig ]; then
    echo "❌ 当前目录不是 Linux 内核源码目录"
    exit 1
fi

# 标记是否做了修改
MODIFIED=0

echo "🧩 开始处理内核版本名设置..."

# 设置 EXTRAVERSION（前缀）
if [ -n "$EXTRAVERSION" ]; then
    echo "  ➤ 设置 EXTRAVERSION = '$EXTRAVERSION'"
    sed -i -E "s|^(EXTRAVERSION\s*=).*|\1 $EXTRAVERSION|" Makefile
    MODIFIED=1
else
    echo "  ➤ 未指定 EXTRAVERSION，保持不变"
fi

# 设置 CONFIG_LOCALVERSION（后缀）
if [ -n "$LOCALVERSION" ]; then
    echo "  ➤ 设置 CONFIG_LOCALVERSION = '$LOCALVERSION'"
    if ! grep -q "^CONFIG_LOCALVERSION=" .config; then
        echo "CONFIG_LOCALVERSION=\"$LOCALVERSION\"" >> .config
    else
        sed -i "s|^CONFIG_LOCALVERSION=.*|CONFIG_LOCALVERSION=\"$LOCALVERSION\"|" .config
    fi
    MODIFIED=1
else
    echo "  ➤ 未指定 CONFIG_LOCALVERSION，保持不变"
fi

# 应用新配置（如果修改过）
if [ "$MODIFIED" -eq 1 ]; then
    echo "  🔁 重新应用配置..."
    make olddefconfig > /dev/null
fi

# 获取最终内核版本名
FINAL_VERSION=$(make kernelrelease)

echo
echo "✅ 最终将编译出的内核版本为："
echo
echo "    $FINAL_VERSION"
echo
