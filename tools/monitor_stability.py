#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitor_stability.py

在典型业务场景（periodic_server + periodic_client）运行期间，
周期性采集 CPU、内存、负载和关键进程状态，展示系统长时间运行的稳定性。

用法示例：
    python3 monitor_stability.py --interval 60 --samples 480 --output TC-R-01-monitor.csv

上述命令表示：每 60 秒采样一次，共采 480 次（约 8 小时）。
"""

import argparse
import subprocess
import time
import os
import sys
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Monitor CPU/Mem and app processes")
    parser.add_argument("--interval", type=int, default=60,
                        help="采样周期，单位秒，默认 60s")
    parser.add_argument("--samples", type=int, default=60,
                        help="采样次数，默认 60 次")
    parser.add_argument("--output", default="monitor.csv",
                        help="输出 CSV 文件名，默认 monitor.csv")
    parser.add_argument("--server-name", default="periodic_server",
                        help="服务端进程名（pgrep -f 匹配），默认 periodic_server")
    parser.add_argument("--client-name", default="periodic_client",
                        help="客户端进程名（pgrep -f 匹配），默认 periodic_client")
    return parser.parse_args()


# ---------- CPU 使用率（基于 /proc/stat） ----------

def read_cpu_times():
    """返回 (idle, total) jiffies"""
    with open("/proc/stat", "r") as f:
        line = f.readline()
    if not line.startswith("cpu "):
        raise RuntimeError("unexpected /proc/stat format")

    parts = line.split()
    # user, nice, system, idle, iowait, irq, softirq, steal, ...
    values = [int(x) for x in parts[1:]]
    idle = values[3] + values[4]  # idle + iowait
    total = sum(values)
    return idle, total


def calc_cpu_usage(prev_idle, prev_total, curr_idle, curr_total):
    idle_delta = curr_idle - prev_idle
    total_delta = curr_total - prev_total
    if total_delta <= 0:
        return 0.0
    usage = 100.0 * (total_delta - idle_delta) / total_delta
    return max(0.0, min(usage, 100.0))


# ---------- 内存信息（基于 /proc/meminfo） ----------

def read_mem_info_mb():
    """返回 (total_mb, used_mb, used_percent)"""
    mem_total = None
    mem_available = None
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1])  # kB
            elif line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1])
            if mem_total is not None and mem_available is not None:
                break

    if mem_total is None or mem_available is None:
        raise RuntimeError("cannot parse /proc/meminfo")

    total_mb = mem_total / 1024.0
    used_mb = (mem_total - mem_available) / 1024.0
    used_percent = 100.0 * used_mb / total_mb if total_mb > 0 else 0.0
    return total_mb, used_mb, used_percent


# ---------- 负载 & 进程检查 ----------

def read_loadavg():
    """返回 1 分钟 loadavg"""
    try:
        load1, load5, load15 = os.getloadavg()
        return load1, load5, load15
    except (AttributeError, OSError):
        # 某些极端系统可能没有 getloadavg
        with open("/proc/loadavg", "r") as f:
            parts = f.read().split()
        load1 = float(parts[0])
        load5 = float(parts[1])
        load15 = float(parts[2])
        return load1, load5, load15


def check_process_alive(pattern):
    """
    使用 pgrep -f pattern 检查进程是否存在。
    返回 1 表示存在，0 表示不存在或 pgrep 不可用。
    """
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return 1 if result.returncode == 0 else 0
    except FileNotFoundError:
        # 系统没有安装 pgrep，则无法检测
        return -1


# ---------- 主逻辑 ----------

def main():
    args = parse_args()

    # 初始化 CPU 计数
    prev_idle, prev_total = read_cpu_times()

    # 打开输出文件并写表头
    first = not os.path.exists(args.output)
    try:
        f = open(args.output, "a", buffering=1)
    except OSError as e:
        print(f"打开输出文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    if first:
        f.write("timestamp,cpu_usage_percent,load1,mem_used_mb,mem_total_mb,"
                "mem_used_percent,server_alive,client_alive\n")

    print(f"开始监控：每 {args.interval} 秒采样一次，共 {args.samples} 次")
    print(f"输出文件: {args.output}")
    print("按 Ctrl+C 可提前结束。\n")

    try:
        for i in range(args.samples):
            t0 = time.time()

            # CPU
            curr_idle, curr_total = read_cpu_times()
            cpu_usage = calc_cpu_usage(prev_idle, prev_total, curr_idle, curr_total)
            prev_idle, prev_total = curr_idle, curr_total

            # 内存
            mem_total_mb, mem_used_mb, mem_used_percent = read_mem_info_mb()

            # 负载
            load1, load5, load15 = read_loadavg()

            # 进程存活情况
            server_alive = check_process_alive(args.server_name)
            client_alive = check_process_alive(args.client_name)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 写入 CSV
            line = (
                f"{now},{cpu_usage:.2f},{load1:.2f},"
                f"{mem_used_mb:.1f},{mem_total_mb:.1f},{mem_used_percent:.2f},"
                f"{server_alive},{client_alive}\n"
            )
            f.write(line)

            # 同时在终端打印一行，方便截图
            print(
                f"[{now}] CPU={cpu_usage:5.2f}%  "
                f"Load1={load1:4.2f}  "
                f"Mem={mem_used_mb:6.1f}/{mem_total_mb:6.1f} MB "
                f"({mem_used_percent:5.2f}%)  "
                f"server_alive={server_alive} client_alive={client_alive}"
            )

            # 睡眠到下一个采样点
            elapsed = time.time() - t0
            sleep_time = args.interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n监控被手动中断。")
    finally:
        f.close()
        print(f"\n监控结束，数据已写入 {args.output}")


if __name__ == "__main__":
    main()
