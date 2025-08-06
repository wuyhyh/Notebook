非常好！我们来增强脚本逻辑，使得：

* 即使你不提供前缀或后缀参数，脚本也能正确运行
* 如果不指定 `CONFIG_LOCALVERSION` 和 `EXTRAVERSION`，就保持原样（不修改）
* 同时仍然会显示最终内核版本号

---

## ✅ 最终增强版脚本：`set_kernel_name.sh`

```bash
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
```

---

## ✅ 使用方式与效果

### 默认运行（不改动版本名）：

```bash
./set_kernel_name.sh
```

输出：

```
未指定 EXTRAVERSION，保持不变
未指定 CONFIG_LOCALVERSION，保持不变
✅ 最终将编译出的内核版本为：6.6.0
```

---

### 设置后缀名：

```bash
./set_kernel_name.sh -debug
```

结果：`6.6.0-debug`

---

### 设置后缀和前缀：

```bash
./set_kernel_name.sh -debug -my
```

结果：`6.6.0-my-debug`

---

## ✅ 总结

| 场景     | 命令                                | 效果               |
|--------|-----------------------------------|------------------|
| 不修改版本名 | `./set_kernel_name.sh`            | 仅回显当前版本          |
| 设置后缀   | `./set_kernel_name.sh -test`      | `6.x.x-test`     |
| 设置前后缀  | `./set_kernel_name.sh -test -exp` | `6.x.x-exp-test` |

---

如你希望进一步将这个脚本集成到 `rpm-pkg` 构建流程中，让它自动使用这个版本号，我可以直接帮你合并两个脚本。是否需要？
