#!/usr/bin/env bash
# preview.sh — 本地预览 Sphinx 静态站点（macOS / Linux / Windows Git Bash）
# 特点：不依赖 sleep；等端口真的可访问再自动打开浏览器

set -euo pipefail

# ===== 可用环境变量覆盖 =====
PORT="${PORT:-8000}"                 # 端口：PORT=9000 ./preview.sh
SITE_DIR="${SITE_DIR:-site}"         # 目录：SITE_DIR=_build/html ./preview.sh
DEBUG="${PREVIEW_DEBUG:-1}"          # 调试：PREVIEW_DEBUG=1 ./preview.sh
# ===========================

log() { [[ "$DEBUG" = "1" ]] && echo "[preview] $*"; }
die() { echo "❌ $*"; exit 1; }

# 解析路径
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SITE_PATH="${ROOT_DIR}/${SITE_DIR}"
[[ -f "$SITE_PATH/index.html" ]] || die "${SITE_PATH}/index.html 不存在；先构建：sphinx-build -b html docs/source ${SITE_DIR}"

# 挑选 Python
if command -v py >/dev/null 2>&1; then PY=(py -3)
elif command -v python3 >/dev/null 2>&1; then PY=(python3)
elif command -v python >/dev/null 2>&1; then PY=(python)
else die "未找到 python/py"; fi
log "Python: ${PY[*]}"

URL="http://127.0.0.1:${PORT}/"
echo "🌐 Serving ${SITE_PATH}"
echo "👉 打开：${URL}"
echo "   退出：Ctrl+C"

open_url() {
  local url="$1"
  case "$(uname -s)" in
    Darwin) open "$url" >/dev/null 2>&1 || true ;;
    Linux)  command -v xdg-open >/dev/null 2>&1 && xdg-open "$url" >/dev/null 2>&1 || true ;;
    MINGW*|MSYS*|CYGWIN*)
      if command -v powershell.exe >/dev/null 2>&1; then
        powershell.exe -NoProfile -Command "Start-Process '$url'" >/dev/null 2>&1 && return 0
      fi
      cmd.exe /c start "" "$url" >/dev/null 2>&1 && return 0
      explorer.exe "$url" >/dev/null 2>&1 || true
      ;;
    *) : ;;
  esac
}

probe_then_open() {
  # 在后台探测端口就绪，再打开浏览器。即使失败也不会中断（set +e）。
  (
    set +e
    # 优先用 curl 探测；没有 curl 就退化为固定等待 2 秒再开
    if command -v curl >/dev/null 2>&1; then
      for i in $(seq 1 15); do   # 最多等 ~15 秒
        if curl -sSfI "$URL" >/dev/null 2>&1; then
          log "probe ok at try $i"
          open_url "$URL"
          exit 0
        fi
        [[ "$DEBUG" = "1" ]] && echo "[preview] probe $i..."
        sleep 1
      done
      # 超时也尝试打开一次（有时浏览器会自己重试）
      open_url "$URL"
    else
      # 没有 curl 的兜底
      sleep 2
      open_url "$URL"
    fi
  ) &
}

# 启动：先并发探测，再以前台运行 http.server（Ctrl+C 可退出）
(
  cd "$SITE_PATH"
  probe_then_open
  # Python 3.7+ 支持 -d；这里已 cd 进入目录，兼容旧版
  "${PY[@]}" -m http.server "$PORT"
)
