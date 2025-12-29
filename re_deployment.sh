#!/usr/bin/env bash
set -euo pipefail

REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_HOST="${REMOTE_HOST:-192.168.1.102}"
REMOTE_DIR="${REMOTE_DIR:-/srv/www/notebook}"

BUILD_SCRIPT="${BUILD_SCRIPT:-./build.sh}"
LOCAL_SITE_DIR="${LOCAL_SITE_DIR:-./site}"

TS="$(date +%Y%m%d-%H%M%S)"
# 临时目录放到 /srv/www 下，避免从 /tmp 搬过来导致 SELinux 标签不对
REMOTE_TMP="/srv/www/.tmp-notebook-site-${TS}"

echo "[INFO] Build..."
"$BUILD_SCRIPT"

case "${REMOTE_DIR%/}" in
  "/srv/www/notebook") ;;
  *) echo "[ERROR] REMOTE_DIR must be /srv/www/notebook"; exit 1;;
esac

echo "[INFO] Prepare remote temp dir: ${REMOTE_TMP}"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "set -e;
  sudo mkdir -p '${REMOTE_TMP}';
  sudo rm -rf '${REMOTE_TMP:?}/'*;
  sudo mkdir -p '${REMOTE_DIR}';
"

echo "[INFO] Upload..."
scp -r "${LOCAL_SITE_DIR}/"* "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_TMP}/"

echo "[INFO] Atomic swap + fix selinux/perm..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" "set -e;
  sudo rm -rf '${REMOTE_DIR}.old' 2>/dev/null || true;
  sudo mv '${REMOTE_DIR}' '${REMOTE_DIR}.old' 2>/dev/null || true;
  sudo mv '${REMOTE_TMP}' '${REMOTE_DIR}';

  # 修复 SELinux 标签（关键，解决 403）
  sudo restorecon -Rv '${REMOTE_DIR}' >/dev/null 2>&1 || true;

  # 修复权限（确保 nginx 可读）
  sudo chown -R nginx:nginx '${REMOTE_DIR}' || true;
  sudo find '${REMOTE_DIR}' -type d -exec chmod 755 {} \; || true;
  sudo find '${REMOTE_DIR}' -type f -exec chmod 644 {} \; || true;

  sudo rm -rf '${REMOTE_DIR}.old' 2>/dev/null || true;
"

echo "[INFO] Done: http://${REMOTE_HOST}:8081/"
