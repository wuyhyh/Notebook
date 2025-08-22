#!/usr/bin/env bash
# 通用本地备份脚本（Git Bash / Linux / macOS 皆可用）

# === 配置部分 ===
# 远程服务器配置
REMOTE_USER="root"                  # 用户名
REMOTE_HOST="192.168.1.6"        # IP 或域名
REMOTE_DIR="/srv/www/notebook/"     # 部署路径

# 本地配置
BUILD_SCRIPT="./build.sh"
LOCAL_SITE_DIR="site/*"

# === 执行部分 ===
# 1. 编译文档
if [ -x "$BUILD_SCRIPT" ]; then
    $BUILD_SCRIPT
else
    echo "错误: 找不到或无法执行 $BUILD_SCRIPT"
    exit 1
fi

# 2. 部署到远程服务器
scp -r $LOCAL_SITE_DIR ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}
