#!/usr/bin/env bash
# 通用本地构建脚本（Git Bash / Linux / macOS 皆可用）

# 出错时立即退出
set -e

# 定义目录
OUTDIR="./site"
SRCDIR="docs/source"
STATICDIR="$SRCDIR/_static/files"

# 定义正则（默认只处理 .bin 文件，可以改成 '.*' 处理所有文件）
REGEX='.*\.bin$'

echo "[INFO] 清理旧的构建目录..."
rm -rf "$OUTDIR"

echo "[INFO] 生成 SHA256 校验文件 (pattern: $REGEX)..."
python tools/make_sha256.py "$STATICDIR" "$REGEX"

echo "[INFO] 使用 Sphinx 构建 HTML..."
sphinx-build -b html "$SRCDIR" "$OUTDIR" -a -E -v

echo "[INFO] 构建完成，输出目录：$OUTDIR"
