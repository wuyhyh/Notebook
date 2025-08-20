#!/usr/bin/env bash
# 通用本地备份脚本（Git Bash / Linux / macOS 皆可用）
# 功能：
# 1) 在当前项目的使用者的用户目录(~)下创建 ~/git-backups/<project>.git 裸仓库
# 2) 将该裸仓库添加为远程 "backup"（已存在则更新 URL）
# 3) 首次推送所有分支与标签到该本地远程
# 4) 输出发生的操作与结果说明
#
# 用法：在项目根目录执行 ./backup.sh
# 先决条件：当前目录必须是一个已有提交的 Git 仓库

set -euo pipefail

# -------- 基础检查 --------
if ! command -v git >/dev/null 2>&1; then
  echo "错误：未找到 git，请先安装 Git（含 Git Bash）。"
  exit 1
fi

# 确保在 git 仓库内执行
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "错误：当前目录不是 Git 仓库。请在项目根目录执行 ./backup.sh"
  exit 1
fi

# 确保有至少一个提交（避免推送空仓库）
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  cat <<'EOF'
错误：当前仓库还没有任何提交。
请先执行至少一次提交，例如：
  git add -A
  git commit -m "initial commit"
然后再运行 ./backup.sh
EOF
  exit 1
fi

# -------- 解析路径与名称 --------
# 用户主目录（Git Bash 下通常类似 /c/Users/<name>）
HOME_DIR="${HOME:-${USERPROFILE:-}}"
if [[ -z "${HOME_DIR}" ]]; then
  echo "错误：无法确定用户主目录（HOME/USERPROFILE 未设置）。"
  exit 1
fi

# 项目顶层目录与项目名
TOPLEVEL="$(git rev-parse --show-toplevel)"
PROJECT_NAME="$(basename "$TOPLEVEL")"

# 备份目录与裸仓库目标路径
BACKUP_ROOT="${HOME_DIR}/git-backups"
TARGET_BARE="${BACKUP_ROOT}/${PROJECT_NAME}.git"

# 远程名可按需修改
REMOTE_NAME="backup"

# -------- 创建裸仓库 --------
mkdir -p "$BACKUP_ROOT"

if [[ ! -d "$TARGET_BARE" ]]; then
  echo "创建本地裸仓库：$TARGET_BARE"
  git init --bare "$TARGET_BARE" >/dev/null
else
  echo "发现已存在的本地裸仓库：$TARGET_BARE"
fi

# -------- 添加/更新远程并推送 --------
# 如已存在同名远程，则更新其 URL；否则新增
if git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  CURRENT_URL="$(git remote get-url "$REMOTE_NAME")"
  if [[ "$CURRENT_URL" != "$TARGET_BARE" ]]; then
    echo "更新远程 \"$REMOTE_NAME\" 的 URL -> $TARGET_BARE"
    git remote set-url "$REMOTE_NAME" "$TARGET_BARE"
  else
    echo "远程 \"$REMOTE_NAME\" 已指向目标：$TARGET_BARE"
  fi
else
  echo "添加远程 \"$REMOTE_NAME\" -> $TARGET_BARE"
  git remote add "$REMOTE_NAME" "$TARGET_BARE"
fi

echo "推送所有分支到本地远程 \"$REMOTE_NAME\" ..."
git push "$REMOTE_NAME" --all

echo "推送所有标签到本地远程 \"$REMOTE_NAME\" ..."
# 若无标签不会报错
git push "$REMOTE_NAME" --tags

# -------- 结果汇总 --------
# 统计分支与标签
mapfile -t BRANCHES < <(git for-each-ref --format='%(refname:short)' refs/heads | sort)
mapfile -t TAGS < <(git for-each-ref --format='%(refname:short)' refs/tags | sort)

echo
echo "================ 备份完成 ================"
echo "项目名            ：${PROJECT_NAME}"
echo "项目位置          ：${TOPLEVEL}"
echo "本地备份仓库(裸)  ：${TARGET_BARE}"
echo "远程名            ：${REMOTE_NAME}"
echo
echo "已推送的分支列表："
if ((${#BRANCHES[@]})); then
  for b in "${BRANCHES[@]}"; do echo "  - $b"; done
else
  echo "  (无本地分支)"
fi
echo
echo "已推送的标签列表："
if ((${#TAGS[@]})); then
  for t in "${TAGS[@]}"; do echo "  - $t"; done
else
  echo "  (无标签)"
fi
echo "=========================================="
echo
cat <<EOF
说明：
1) 已在你的用户目录下创建（或复用）本地裸仓库作为“备份远程”：
     ${TARGET_BARE}

2) 当前仓库已将所有分支与标签推送到该远程：
     远程名：${REMOTE_NAME}

3) 之后可随时执行：
     git push ${REMOTE_NAME} --all
     git push ${REMOTE_NAME} --tags
   以增量更新本地备份。

4) 如需从备份恢复，可在任意位置运行：
     git clone "${TARGET_BARE}" "<你的新工作目录>"
EOF
