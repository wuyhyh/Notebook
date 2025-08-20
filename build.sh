#!/usr/bin/env bash
# 通用本地备份脚本（Git Bash / Linux / macOS 皆可用）

rm -rf ./site

sphinx-build -b html docs/source site -a -E
