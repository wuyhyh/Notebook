#!/usr/bin/env bash
set -euo pipefail

# -------- Config ----------
PORT="${PORT:-8000}"                 # 可用 PORT=9000 覆盖
SITE_DIR="${SITE_DIR:-site}"         # 产物目录
# --------------------------

# 解析脚本所在位置，支持任意目录调用
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_PATH="${ROOT_DIR}/${SITE_DIR}"

if [[ ! -d "$SITE_PATH" || ! -f "$SITE_PATH/index.html" ]]; then
  echo "❌ 没找到 ${SITE_PATH}/index.html ；先构建："
  echo "   sphinx-build -b html docs/source ${SITE_DIR}"
  exit 1
fi

# 选择可用的 Python
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo "❌ 未找到 python / python3"
  exit 1
fi

URL="http://127.0.0.1:${PORT}/"

echo "🌐 Serving ${SITE_PATH} at ${URL}"
echo "   退出：Ctrl+C"

# 自动在默认浏览器打开
open_url () {
  case "$(uname -s)" in
    Darwin)  open "$URL" ;;
    Linux)   xdg-open "$URL" >/dev/null 2>&1 || true ;;
    *)       : ;;
  esac
}

# 进入站点目录并启动
(cd "$SITE_PATH" && { open_url & "$PY" -m http.server "$PORT"; })
