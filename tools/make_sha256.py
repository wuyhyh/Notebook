#!/usr/bin/env python3
import os
import sys
import re
import hashlib

def sha256sum(path: str) -> str:
    """计算单个文件的 SHA256 值"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def process_file(filepath: str):
    """为单个文件生成 .sha256"""
    if not os.path.isfile(filepath):
        print(f"[WARN] 不是普通文件，跳过: {filepath}")
        return
    if filepath.endswith(".sha256"):
        return
    sha = sha256sum(filepath)
    sha_file = filepath + ".sha256"
    with open(sha_file, "w") as f:
        f.write(sha + "\n")
    print(f"[OK] 生成 {sha_file}: {sha}")

def process_dir(target_dir: str, pattern: str):
    """为目录下符合正则的文件生成 .sha256"""
    if not os.path.isdir(target_dir):
        print(f"[ERROR] 目录不存在: {target_dir}")
        sys.exit(1)
    regex = re.compile(pattern)
    matched = False
    for filename in os.listdir(target_dir):
        filepath = os.path.join(target_dir, filename)
        if not os.path.isfile(filepath) or filename.endswith(".sha256"):
            continue
        if not regex.match(filename):
            continue
        process_file(filepath)
        matched = True
    if not matched:
        print(f"[WARN] 没有匹配到任何文件 (pattern: {pattern})")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # 单文件模式
        target_file = sys.argv[1]
        process_file(target_file)
    elif len(sys.argv) == 3:
        # 目录 + 正则模式
        target_dir = sys.argv[1]
        pattern = sys.argv[2]
        process_dir(target_dir, pattern)
    else:
        print("用法:")
        print("  单文件模式: make_sha256.py <文件路径>")
        print("  目录模式:   make_sha256.py <目标目录> <正则表达式>")
        print("示例:")
        print("  make_sha256.py docs/source/_static/files/fip-all.bin")
        print("  make_sha256.py docs/source/_static/files '.*\\.bin$'")
        sys.exit(1)
