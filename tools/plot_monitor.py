#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot CPU / Memory / Process liveness curves from long-run monitor CSV files.

Example:
    python3 plot_monitor.py TC-R-01-monitor.csv TC-R-01-monitor-8h.csv -o plots

This will generate in 'plots/' directory:
    TC-R-01-monitor_cpu_usage.png
    TC-R-01-monitor_mem_usage.png
    TC-R-01-monitor_alive.png
    TC-R-01-monitor-8h_cpu_usage.png
    TC-R-01-monitor-8h_mem_usage.png
    TC-R-01-monitor-8h_alive.png
"""

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_single_file(csv_path: str, output_dir: str) -> None:
    basename = os.path.basename(csv_path)
    name, _ = os.path.splitext(basename)

    df = pd.read_csv(csv_path)
    if "timestamp" not in df.columns:
        raise ValueError(f"{csv_path!r} missing 'timestamp' column")

    # convert to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # ---------- CPU usage ----------
    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["cpu_usage_percent"])
    ax.set_title(f"CPU Usage over Time ({name})")
    ax.set_xlabel("Time")
    ax.set_ylabel("CPU Usage (%)")
    fig.autofmt_xdate()
    out_cpu = os.path.join(output_dir, f"{name}_cpu_usage.png")
    fig.tight_layout()
    fig.savefig(out_cpu, dpi=150)
    plt.close(fig)

    # ---------- Memory usage ----------
    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["mem_used_percent"])
    ax.set_title(f"Memory Usage over Time ({name})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Memory Usage (%)")
    fig.autofmt_xdate()
    out_mem = os.path.join(output_dir, f"{name}_mem_usage.png")
    fig.tight_layout()
    fig.savefig(out_mem, dpi=150)
    plt.close(fig)

    # ---------- Process liveness (0/1) ----------
    if "server_alive" in df.columns and "client_alive" in df.columns:
        fig, ax = plt.subplots()
        ax.step(df["timestamp"], df["server_alive"],
                where="post", label="server_alive")
        ax.step(df["timestamp"], df["client_alive"],
                where="post", label="client_alive")
        ax.set_title(f"Process Liveness ({name})")
        ax.set_xlabel("Time")
        ax.set_ylabel("Alive (0/1)")
        ax.set_yticks([0, 1])
        ax.legend()
        fig.autofmt_xdate()
        out_alive = os.path.join(output_dir, f"{name}_alive.png")
        fig.tight_layout()
        fig.savefig(out_alive, dpi=150)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot CPU/Memory/Process liveness curves from monitor CSV files"
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        help="One or more CSV files, e.g. TC-R-01-monitor.csv TC-R-01-monitor-8h.csv",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="plots",
        help="Output directory for PNG files (default: ./plots)",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for csv_path in args.csv_files:
        print(f"Processing {csv_path!r} ...")
        plot_single_file(csv_path, args.output_dir)

    print(f"Done. Figures saved in: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
