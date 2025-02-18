import heapq
from collections import Counter

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        # 1. 统计每个数字的频率
        count = Counter(nums)

        # 2. 使用堆（最小堆），堆中存储 (频率, 数字) 元组
        # heapq 默认是最小堆，所以我们用负数来模拟最大堆
        # 然后从堆中选出前 k 个频率最高的元素
        return [item[0] for item in heapq.nlargest(k, count.items(), key=lambda x: x[1])]
