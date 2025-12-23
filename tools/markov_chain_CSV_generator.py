import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import io
import sys

class MarkovChainCSVGenerator:
    def __init__(self, csv_content):
        """初始化马尔科夫链生成器"""
        # 使用io.StringIO而不是pandas.compat.StringIO
        self.data = pd.read_csv(io.StringIO(csv_content))
        self.columns = self.data.columns.tolist()

        # 转换时间戳为datetime对象
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])

        # 存储原始数据的统计信息
        self.original_stats = {
            'start_time': self.data['timestamp'].iloc[0],
            'end_time': self.data['timestamp'].iloc[-1],
            'time_interval': self.data['timestamp'].diff().mean().total_seconds(),
            'num_records': len(self.data)
        }

    def calculate_transition_matrix(self, states, num_bins=10):
        """计算状态转移概率矩阵"""
        # 将连续值离散化为状态
        min_val = min(states)
        max_val = max(states)
        bin_size = (max_val - min_val) / num_bins

        # 创建状态标签
        state_labels = []
        state_indices = []

        for val in states:
            bin_index = min(int((val - min_val) / bin_size), num_bins - 1)
            state_labels.append(f"bin_{bin_index}")
            state_indices.append(bin_index)

        # 计算转移矩阵
        transition_matrix = np.zeros((num_bins, num_bins))

        for i in range(len(state_indices) - 1):
            from_state = state_indices[i]
            to_state = state_indices[i + 1]
            transition_matrix[from_state, to_state] += 1

        # 归一化为概率
        row_sums = transition_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # 避免除以零
        transition_matrix = transition_matrix / row_sums

        return transition_matrix, state_labels, min_val, max_val, bin_size

    def generate_markov_sequence(self, initial_state, transition_matrix, length, num_bins):
        """使用马尔科夫链生成新序列"""
        sequence = [initial_state]
        current_state = initial_state

        for _ in range(length - 1):
            # 获取当前状态的转移概率
            probs = transition_matrix[current_state, :]

            # 如果所有概率都是0，随机选择下一个状态
            if probs.sum() == 0:
                next_state = random.randint(0, num_bins - 1)
            else:
                # 根据概率选择下一个状态
                next_state = np.random.choice(range(num_bins), p=probs)

            sequence.append(next_state)
            current_state = next_state

        return sequence

    def convert_to_continuous(self, discrete_sequence, min_val, max_val, bin_size, add_noise=True):
        """将离散状态转换为连续值"""
        continuous_sequence = []

        for state in discrete_sequence:
            # 计算bin的中心值
            center_value = min_val + (state + 0.5) * bin_size

            if add_noise:
                # 添加一些随机噪声使数据更真实
                noise = np.random.normal(0, bin_size * 0.2)
                center_value += noise

            # 确保值在合理范围内
            center_value = max(min_val, min(center_value, max_val))
            continuous_sequence.append(center_value)

        return continuous_sequence

    def generate_extended_data(self, target_hours=8):
        """生成扩展的8小时数据"""
        # 计算需要生成的数据点数
        time_interval = self.original_stats['time_interval']  # 秒
        total_seconds = target_hours * 3600
        num_new_points = int(total_seconds / time_interval)

        # 为每个数值列创建马尔科夫链
        extended_data = {
            'timestamp': [],
            'cpu_usage_percent': [],
            'load1': [],
            'mem_used_mb': [],
            'mem_total_mb': [],
            'mem_used_percent': [],
            'server_alive': [],
            'client_alive': []
        }

        # 创建时间序列（从原始数据结束时间开始）
        last_time = self.original_stats['end_time']

        # 复制一些原始数据以保持连续性
        num_overlap = min(20, len(self.data))  # 重叠20个点
        overlap_data = self.data.iloc[-num_overlap:].copy()

        # 为每个数值特征创建马尔科夫链
        num_bins = 15  # 状态数量

        # 处理CPU使用率
        cpu_states = self.data['cpu_usage_percent'].values
        cpu_transition, cpu_labels, cpu_min, cpu_max, cpu_bin_size = self.calculate_transition_matrix(
            cpu_states, num_bins
        )
        initial_cpu_state = min(num_bins - 1, int((cpu_states[-1] - cpu_min) / cpu_bin_size))
        cpu_sequence = self.generate_markov_sequence(
            initial_cpu_state, cpu_transition, num_new_points, num_bins
        )
        cpu_values = self.convert_to_continuous(
            cpu_sequence, cpu_min, cpu_max, cpu_bin_size
        )

        # 处理系统负载
        load_states = self.data['load1'].values
        load_transition, load_labels, load_min, load_max, load_bin_size = self.calculate_transition_matrix(
            load_states, num_bins
        )
        initial_load_state = min(num_bins - 1, int((load_states[-1] - load_min) / load_bin_size))
        load_sequence = self.generate_markov_sequence(
            initial_load_state, load_transition, num_new_points, num_bins
        )
        load_values = self.convert_to_continuous(
            load_sequence, load_min, load_max, load_bin_size
        )

        # 处理内存使用百分比
        mem_percent_states = self.data['mem_used_percent'].values
        mem_percent_transition, _, mem_percent_min, mem_percent_max, mem_percent_bin_size = self.calculate_transition_matrix(
            mem_percent_states, num_bins
        )
        initial_mem_percent_state = min(num_bins - 1, int((mem_percent_states[-1] - mem_percent_min) / mem_percent_bin_size))
        mem_percent_sequence = self.generate_markov_sequence(
            initial_mem_percent_state, mem_percent_transition, num_new_points, num_bins
        )
        mem_percent_values = self.convert_to_continuous(
            mem_percent_sequence, mem_percent_min, mem_percent_max, mem_percent_bin_size
        )

        # 生成时间戳和填充其他字段
        current_time = last_time
        total_records = len(overlap_data) + num_new_points

        # 添加重叠数据
        for i in range(len(overlap_data)):
            row = overlap_data.iloc[i]
            extended_data['timestamp'].append(row['timestamp'])
            extended_data['cpu_usage_percent'].append(row['cpu_usage_percent'])
            extended_data['load1'].append(row['load1'])
            extended_data['mem_used_mb'].append(row['mem_used_mb'])
            extended_data['mem_total_mb'].append(row['mem_total_mb'])
            extended_data['mem_used_percent'].append(row['mem_used_percent'])
            extended_data['server_alive'].append(row['server_alive'])
            extended_data['client_alive'].append(row['client_alive'])

        # 生成新数据
        for i in range(num_new_points):
            current_time += timedelta(seconds=time_interval)

            # 添加一些周期性变化（模拟白天/夜间模式）
            hour_of_day = current_time.hour
            time_factor = 1.0

            # 白天（8-18点）CPU使用率稍高
            if 8 <= hour_of_day < 18:
                time_factor = 1.1
            # 夜间（0-6点）CPU使用率稍低
            elif 0 <= hour_of_day < 6:
                time_factor = 0.9

            # 计算内存使用量（基于百分比）
            mem_total = 15514.9  # 固定值
            mem_percent = mem_percent_values[i] * time_factor
            mem_used = mem_total * mem_percent / 100

            # 确保值在合理范围内
            cpu_value = max(0.0, min(100.0, cpu_values[i] * time_factor))
            load_value = max(0.0, load_values[i])
            mem_percent = max(0.0, min(100.0, mem_percent))

            # 随机设置server_alive和client_alive（大多数时间正常）
            server_alive = 1
            client_alive = 1

            # 偶尔设置服务异常（1%的概率）
            if random.random() < 0.01:
                server_alive = 0

            if random.random() < 0.02:
                client_alive = 0

            extended_data['timestamp'].append(current_time)
            extended_data['cpu_usage_percent'].append(round(cpu_value, 2))
            extended_data['load1'].append(round(load_value, 2))
            extended_data['mem_used_mb'].append(round(mem_used, 1))
            extended_data['mem_total_mb'].append(round(mem_total, 1))
            extended_data['mem_used_percent'].append(round(mem_percent, 2))
            extended_data['server_alive'].append(server_alive)
            extended_data['client_alive'].append(client_alive)

        return pd.DataFrame(extended_data)

    def save_to_csv(self, df, filename):
        """保存到CSV文件"""
        df.to_csv(filename, index=False)
        print(f"数据已保存到 {filename}")
        print(f"总记录数: {len(df)}")
        print(f"时间范围: {df['timestamp'].iloc[0]} 到 {df['timestamp'].iloc[-1]}")

    def print_summary(self, df):
        """打印数据摘要"""
        print("\n数据摘要:")
        print("=" * 50)
        print(f"总行数: {len(df)}")
        print(f"时间跨度: {(df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds() / 3600:.1f} 小时")
        print(f"时间间隔: {self.original_stats['time_interval']:.0f} 秒")
        print("\n统计信息:")
        print(f"CPU使用率: {df['cpu_usage_percent'].mean():.2f}% ± {df['cpu_usage_percent'].std():.2f}%")
        print(f"系统负载: {df['load1'].mean():.2f} ± {df['load1'].std():.2f}")
        print(f"内存使用率: {df['mem_used_percent'].mean():.2f}% ± {df['mem_used_percent'].std():.2f}%")
        print(f"server_alive正常率: {df['server_alive'].mean() * 100:.1f}%")
        print(f"client_alive正常率: {df['client_alive'].mean() * 100:.1f}%")

# 使用示例 - 从命令行参数读取文件
def main():
    import argparse

    parser = argparse.ArgumentParser(description='使用马尔科夫链扩展监控CSV数据')
    parser.add_argument('input_file', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', default='TC-R-01-monitor-extended-8h.csv',
                        help='输出CSV文件路径（默认：TC-R-01-monitor-extended-8h.csv）')
    parser.add_argument('-t', '--hours', type=float, default=8.0,
                        help='要扩展的小时数（默认：8小时）')

    args = parser.parse_args()

    try:
        # 读取原始CSV内容
        print(f"正在读取文件: {args.input_file}")
        with open(args.input_file, 'r', encoding='utf-8') as f:
            csv_content = f.read()

        # 创建生成器
        generator = MarkovChainCSVGenerator(csv_content)

        print("原始数据分析:")
        print("=" * 50)
        print(f"原始数据记录数: {generator.original_stats['num_records']}")
        print(f"原始时间范围: {generator.original_stats['start_time']} 到 {generator.original_stats['end_time']}")
        print(f"时间间隔: {generator.original_stats['time_interval']:.0f} 秒")

        # 生成扩展数据
        print(f"\n正在生成扩展的{args.hours}小时数据...")
        extended_df = generator.generate_extended_data(target_hours=args.hours)

        # 打印摘要
        generator.print_summary(extended_df)

        # 保存到新文件
        output_filename = args.output
        generator.save_to_csv(extended_df, output_filename)

        # 显示部分数据
        print("\n扩展数据示例:")
        print("=" * 50)
        print("前5行数据:")
        print(extended_df.head().to_string(index=False))
        print("\n后5行数据:")
        print(extended_df.tail().to_string(index=False))

    except FileNotFoundError:
        print(f"错误：找不到文件 {args.input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()