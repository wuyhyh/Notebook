#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_hosts_xplat.py

跨平台 hosts 配置工具：支持 Windows / WSL / macOS / Linux。

目标：把 (IP, HOST/别名) 写入 hosts，同时自动清理旧映射并做备份。

用法示例：
  # Windows（管理员终端）: 更新 Windows hosts，并同步更新 WSL /etc/hosts（如存在）
  python setup_hosts_xplat.py --ip 192.168.1.102 --host rocky-server.lab

  # Linux / macOS / WSL：更新 /etc/hosts（需要 sudo/root）
  sudo python3 setup_hosts_xplat.py --ip 192.168.1.7 --host tokamak-4.home

  # 同时写多个主机名（别名）
  sudo python3 setup_hosts_xplat.py --ip 192.168.1.7 --host tokamak-4.home --host tokamak-4

注意：
  - 在 WSL 里运行默认只改 WSL 自己的 /etc/hosts；不默认修改 Windows hosts。
  - Windows 修改 hosts 需要管理员权限；脚本会尝试自动触发 UAC 提权。
"""

from __future__ import annotations

import argparse
import ipaddress
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

DEFAULT_HOST = "rocky-server"
WIN_HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
UNIX_HOSTS_PATH = "/etc/hosts"


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    """Run a command, never raising FileNotFoundError.
    Returns CompletedProcess with returncode=127 if executable is missing."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as e:
        return subprocess.CompletedProcess(cmd, 127, stdout="", stderr=str(e))


def is_windows() -> bool:
    return os.name == "nt"


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def is_wsl() -> bool:
    if not is_linux():
        return False
    try:
        # 典型包含 "Microsoft" / "WSL2"
        v = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
        return "microsoft" in v or "wsl" in v
    except Exception:
        return False


def is_root() -> bool:
    if is_windows():
        return False
    try:
        return os.geteuid() == 0  # type: ignore[attr-defined]
    except Exception:
        return False


def is_admin() -> bool:
    if not is_windows():
        return False
    try:
        import ctypes  # noqa: F401
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin(python_exe: str, argv: List[str]) -> None:
    """
    Windows: 用 UAC 重新以管理员权限启动同一条命令
    """
    import ctypes

    # argv 是 sys.argv（不含 python），这里我们重建完整命令：python + 脚本参数
    params = " ".join([f'"{a}"' for a in argv])
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
    if rc <= 32:
        print("ERROR: 无法触发管理员提权（UAC）。请手工用“以管理员身份运行”打开终端再执行。", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(0)


def read_text_guess_encoding(p: Path) -> str:
    data = p.read_bytes()
    # Windows hosts 常见：utf-8-sig/utf-8/mbcs；Unix 通常 utf-8
    for enc in ("utf-8-sig", "utf-8", "mbcs"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def write_text_atomic(p: Path, content: str, newline: str) -> None:
    tmp = p.with_suffix(p.suffix + ".tmp")
    # newline 参数会把 \n 转成指定换行符
    tmp.write_text(content, encoding="utf-8", newline=newline)
    tmp.replace(p)


@dataclass(frozen=True)
class HostsUpdateResult:
    hosts_path: Path
    backup_path: Path


def normalize_hosts_list(hosts: Iterable[str]) -> List[str]:
    out: List[str] = []
    for h in hosts:
        h = h.strip()
        if not h:
            continue
        # 允许用户传 "a,b,c"
        parts = [x.strip() for x in h.split(",") if x.strip()]
        out.extend(parts)
    # 去重但保持顺序
    seen = set()
    uniq = []
    for h in out:
        if h not in seen:
            uniq.append(h)
            seen.add(h)
    return uniq


def update_hosts_file(p: Path, ip: str, hosts: List[str], newline: str, dry_run: bool) -> HostsUpdateResult:
    """
    - 备份 hosts
    - 删除所有“非注释行”中包含任一 host 的映射
    - 追加新的 "<ip> <host1> <host2> ..."
    """
    ts = int(time.time())
    backup = p.with_name(f"{p.name}.bak.{ts}")

    original = read_text_guess_encoding(p)
    lines = original.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    # 预编译：对每个 host，匹配“非注释行”中的 token
    host_set = set(hosts)

    new_lines: List[str] = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            new_lines.append(line)
            continue

        tokens = s.split()
        # tokens[0] 是 IP，其余是 host/alias
        if any(tok in host_set for tok in tokens[1:]):
            continue
        new_lines.append(line)

    if new_lines and new_lines[-1].strip() != "":
        new_lines.append("")

    new_lines.append(f"{ip} " + " ".join(hosts))

    new_text = "\n".join(new_lines).rstrip("\n") + "\n"

    if dry_run:
        print(f"DRY-RUN: 将更新 {p}")
        print(f"DRY-RUN: 备份文件将为 {backup}")
        return HostsUpdateResult(hosts_path=p, backup_path=backup)

    shutil.copy2(p, backup)
    write_text_atomic(p, new_text, newline=newline)
    return HostsUpdateResult(hosts_path=p, backup_path=backup)


def flush_dns() -> None:
    """
    尽力刷新本机 DNS cache。失败不致命。
    """
    if is_windows():
        r = run(["ipconfig", "/flushdns"])
        if r.returncode == 0:
            print("OK: ipconfig /flushdns")
        else:
            print("WARNING: ipconfig /flushdns 失败（可忽略）", file=sys.stderr)
        return

    if is_macos():
        # macOS: 两条常见命令
        run(["dscacheutil", "-flushcache"])
        run(["killall", "-HUP", "mDNSResponder"])
        print("OK: macOS DNS cache flush（尽力执行）")
        return

    if is_linux():
        # Linux: 依次尝试几个常见入口
        cmds = [
            ["resolvectl", "flush-caches"],
            ["systemd-resolve", "--flush-caches"],
            ["nscd", "-i", "hosts"],
        ]
        for c in cmds:
            r = run(c)
            if r.returncode == 0:
                print(f"OK: {' '.join(c)}")
                return
        print("INFO: 未找到可用的 DNS cache flush 命令（通常不影响 hosts 生效）")
        return


def wsl_available_on_windows() -> bool:
    r = run(["wsl.exe", "-l", "-q"])
    return r.returncode == 0 and r.stdout.strip() != ""


def update_wsl_hosts_from_windows(ip: str, hosts: List[str], distro: str | None, dry_run: bool) -> None:
    """
    在 Windows 上运行时，顺带更新 WSL 的 /etc/hosts（用 wsl.exe 进入 root 执行）。
    """
    if not wsl_available_on_windows():
        print("INFO: 未检测到 WSL，跳过 WSL /etc/hosts。")
        return

    # 构造一个 shell 脚本：删除旧映射 + 追加新映射（一行写入多个 alias）
    host_alt = " ".join(hosts)
    # grep 过滤：只要行里出现任意 host token，就删掉
    # 用一个 (host1|host2|...) 的正则匹配 token 边界
    pat = "|".join([re.escape(h) for h in hosts])
    cmd = (
        "set -eu; "
        "TS=$(date +%s); "
        "cp /etc/hosts /etc/hosts.bak.$TS; "
        f"grep -vE '^[[:space:]]*[^#].*[[:space:]]({pat})([[:space:]]|$)' /etc/hosts > /tmp/hosts.new; "
        "printf '\\n' >> /tmp/hosts.new; "
        f"printf '{ip} {host_alt}\\n' >> /tmp/hosts.new; "
        "cat /tmp/hosts.new > /etc/hosts; "
        "rm -f /tmp/hosts.new; "
        "echo OK"
    )

    base = ["wsl.exe"]
    if distro:
        base += ["-d", distro]
    base += ["-u", "root", "--", "sh", "-lc", cmd]

    if dry_run:
        print("DRY-RUN: 将在 WSL 执行 /etc/hosts 更新（通过 wsl.exe）")
        return

    r = run(base)
    if r.returncode == 0:
        print("OK: WSL /etc/hosts 已更新")
    else:
        print("WARNING: WSL /etc/hosts 更新失败（不影响 Windows hosts）", file=sys.stderr)
        if r.stdout:
            print(r.stdout, file=sys.stderr)
        if r.stderr:
            print(r.stderr, file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="跨平台 hosts 配置工具（Windows/WSL/macOS/Linux）"
    )
    ap.add_argument("--ip", required=True, help="目标 IP，例如 192.168.1.102")
    ap.add_argument(
        "--host",
        action="append",
        default=[],
        help=f"主机名/别名，可重复指定；默认 {DEFAULT_HOST}",
    )
    ap.add_argument(
        "--no-wsl",
        action="store_true",
        help="Windows 上：不修改 WSL 的 /etc/hosts（默认会尝试修改）",
    )
    ap.add_argument("--wsl-distro", default=None, help="Windows 上：指定 WSL 发行版名称（可选）")
    ap.add_argument(
        "--hosts-file",
        default=None,
        help="指定 hosts 文件路径（高级用法）。默认 Windows 用系统 hosts，Unix 用 /etc/hosts",
    )
    ap.add_argument("--dry-run", action="store_true", help="演练模式：不写入文件，只打印将要做的事")
    args = ap.parse_args()

    # 校验 IP
    try:
        ipaddress.ip_address(args.ip)
    except ValueError:
        print(f"ERROR: 非法 IP: {args.ip}", file=sys.stderr)
        return 1

    hosts = normalize_hosts_list(args.host)
    if not hosts:
        hosts = [DEFAULT_HOST]

    # 选择 hosts 路径和换行符
    if args.hosts_file:
        hosts_path = Path(args.hosts_file)
    else:
        hosts_path = Path(WIN_HOSTS_PATH) if is_windows() else Path(UNIX_HOSTS_PATH)

    newline = "\r\n" if is_windows() else "\n"

    # 权限检查
    if is_windows():
        if not is_admin():
            # 自动提权：python.exe + (脚本路径 + 原始参数)
            relaunch_as_admin(sys.executable, sys.argv)
        # Windows hosts 可能被只读属性误设，尽力去掉（不保证）
        run(["attrib", "-r", str(hosts_path)])
    else:
        if not is_root():
            print("ERROR: 修改 /etc/hosts 需要 root 权限。请用 sudo 运行。", file=sys.stderr)
            return 2

    if not hosts_path.exists():
        print(f"ERROR: hosts 文件不存在：{hosts_path}", file=sys.stderr)
        return 3

    # 更新 hosts
    try:
        res = update_hosts_file(hosts_path, args.ip, hosts, newline=newline, dry_run=args.dry_run)
        print(f"OK: hosts 已更新：{args.ip} {' '.join(hosts)}")
        print(f"OK: 备份：{res.backup_path}")
    except PermissionError as e:
        print("ERROR: 写 hosts 被拒绝。", file=sys.stderr)
        print(f"DETAIL: {e}", file=sys.stderr)
        return 4

    # DNS flush（尽力）
    flush_dns()

    # Windows: 可选更新 WSL /etc/hosts
    if is_windows() and not args.no_wsl:
        update_wsl_hosts_from_windows(args.ip, hosts, args.wsl_distro, dry_run=args.dry_run)

    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
