import heapq

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        # 使用最小堆，堆的大小为 k
        min_heap = []

        # 遍历数组中的每个数
        for num in nums:
            # 将当前数加入堆
            heapq.heappush(min_heap, num)
            # 如果堆的大小超过 k，弹出堆顶元素
            if len(min_heap) > k:
                heapq.heappop(min_heap)

        # 堆顶元素即为第 k 个最大的元素
        return min_heap[0]
