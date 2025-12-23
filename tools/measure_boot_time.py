#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 Windows 上运行，通过串口测量系统启动时间。

使用方法示例：
    python measure_boot_time.py --port COM3 --baud 115200 --keyword "APP READY" --show

步骤：
1. 先运行本脚本；
2. 再给开发板上电或按复位；
3. 脚本会在收到第一行串口输出时记录 T0，在检测到包含关键字的行时记录 T1；
4. 打印启动时间 T1 - T0。
"""

import argparse
import time
import sys

import serial


def parse_args():
    parser = argparse.ArgumentParser(description="Measure boot time via serial port")
    parser.add_argument(
        "--port", required=True,
        help="串口号，例如 COM3 / COM4"
    )
    parser.add_argument(
        "--baud", type=int, default=115200,
        help="波特率，默认 115200"
    )
    parser.add_argument(
        "--keyword", default="APP READY",
        help="表示系统启动完成的关键字，默认 'APP READY'"
    )
    parser.add_argument(
        "--timeout", type=float, default=300.0,
        help="最长等待时间（秒），默认 300 秒"
    )
    parser.add_argument(
        "--show", action="store_true",
        help="在终端实时打印串口输出"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            timeout=0.1,  # 100ms 轮询
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
    except Exception as e:
        print(f"打开串口失败: {e}")
        sys.exit(1)

    print(f"已打开串口 {args.port}，波特率 {args.baud}")
    print("请现在给板子上电或按复位，开始捕获启动过程...\n")

    # 清空缓冲区，避免旧数据干扰
    ser.reset_input_buffer()

    start_time = None  # T0
    end_time = None  # T1

    t_begin_wait = time.monotonic()

    try:
        while True:
            if time.monotonic() - t_begin_wait > args.timeout:
                print(f"超过最大等待时间 {args.timeout} 秒，仍未检测到关键字 '{args.keyword}'，退出。")
                break

            line = ser.readline()
            if not line:
                continue

            # 解码为字符串
            try:
                text = line.decode("utf-8", errors="replace").rstrip("\r\n")
            except Exception:
                text = repr(line)

            # 第一次收到非空行，认为是启动开始
            if start_time is None:
                start_time = time.monotonic()
                wall = time.strftime("%H:%M:%S", time.localtime())
                print(f"[{wall}] 检测到第一行串口输出，视为启动开始 (T0)")
                print(f"首行内容: {text}")

            # 打印串口内容（可选）
            if args.show:
                print(text)

            # 检查是否包含关键字
            if args.keyword in text:
                end_time = time.monotonic()
                wall = time.strftime("%H:%M:%S", time.localtime())
                print(f"\n[{wall}] 检测到关键字 '{args.keyword}' (T1)")
                break

    except KeyboardInterrupt:
        print("\n用户中断测试。")
    finally:
        ser.close()

    if start_time is not None and end_time is not None:
        delta = end_time - start_time - 4
        print(f"\n启动时间（T1 - T0）≈ {delta:.3f} 秒")
    else:
        print("\n未能完整测得启动时间。")


if __name__ == "__main__":
    main()
