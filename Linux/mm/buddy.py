import math

class BuddyAllocator:
    def __init__(self, max_order):
        """
        初始化伙伴系统
        :param max_order: 最大阶数，控制最大块大小 2^max_order
        """
        self.max_order = max_order
        self.memory_size = 1 << max_order  # 总内存大小
        self.free_lists = {i: [] for i in range(max_order + 1)}  # 存储空闲块

        # 初始化时，将整个内存块作为最大阶的空闲块
        self.free_lists[max_order].append(0)

    def allocate(self, size):
        """
        分配内存
        :param size: 需要的最小块大小
        :return: 返回分配的块地址
        """
        order = math.ceil(math.log2(size))  # 计算合适的 order
        if order > self.max_order:
            print(f"请求大小 {size} 超出最大支持的块大小！")
            return None

        # 找到最小的可用阶
        for o in range(order, self.max_order + 1):
            if self.free_lists[o]:
                addr = self.free_lists[o].pop(0)  # 取出一个空闲块

                # 需要拆分到目标 order
                while o > order:
                    o -= 1
                    buddy_addr = addr + (1 << o)  # 计算伙伴地址
                    self.free_lists[o].append(buddy_addr)  # 伙伴块放入更小阶

                print(f"分配成功: 大小 {size} (阶 {order})，地址 {addr}")
                return addr

        print("内存不足，分配失败！")
        return None

    def free(self, addr, size):
        """
        释放内存
        :param addr: 释放的起始地址
        :param size: 释放块的大小
        """
        order = math.ceil(math.log2(size))  # 计算阶数

        while order <= self.max_order:
            buddy_addr = addr ^ (1 << order)  # 计算伙伴块地址

            # 查找伙伴是否空闲
            if buddy_addr in self.free_lists[order]:
                self.free_lists[order].remove(buddy_addr)  # 移除伙伴块
                addr = min(addr, buddy_addr)  # 合并后块地址取较小值
                order += 1  # 合并成更高阶
                print(f"合并: 地址 {addr}, 新阶 {order}")
            else:
                break  # 伙伴不空闲，不能合并

        self.free_lists[order].append(addr)  # 插入空闲块
        print(f"释放: 地址 {addr}, 阶 {order}")

    def display(self):
        """图形化显示内存状态"""
        print("\n内存状态图:")
        print("=" * (self.memory_size * 2))

        # 初始化内存表示，默认所有块都占用
        memory_map = ["■"] * self.memory_size

        # 标记空闲块
        for order in self.free_lists:
            for addr in self.free_lists[order]:
                block_size = 1 << order
                for i in range(block_size):
                    memory_map[addr + i] = "□"  # 用 "□" 表示空闲块

        # 以 16 个单位为一行，直观显示内存状态
        for i in range(0, self.memory_size, 16):
            chunk = "".join(memory_map[i:i + 16])
            print(f"{i:4d}: {chunk}")

        print("=" * (self.memory_size * 2))
        print("□: 空闲块  ■: 已占用块")
        print("-" * 40)


# 示例运行
allocator = BuddyAllocator(max_order=4)  # 16 单位大小的内存
allocator.display()

addr1 = allocator.allocate(4)  # 分配 4 单位块
allocator.display()

addr2 = allocator.allocate(2)  # 分配 2 单位块
allocator.display()

allocator.free(addr1, 4)  # 释放 4 单位块
allocator.display()

addr3 = allocator.allocate(2)  # 分配 2 单位块
allocator.display()

addr4 = allocator.allocate(8)  # 分配 8 单位块
allocator.display()

allocator.free(addr4, 2)  # 释放 2 单位块
allocator.display()
