import heapq


class MedianFinder:
    def __init__(self):
        """ 初始化最大堆和最小堆 """
        self.left_max_heap = []
        self.right_min_heap = []

    def addNum(self, num: int) -> None:
        """ 插入一个新数 """
        heapq.heappush(self.left_max_heap, -num)  # 先加入最大堆，用取相反数来模拟

        # 维护最大堆和最小堆
        # 把最大堆的堆顶放入最小堆
        max_left = - heapq.heappop(self.left_max_heap)
        heapq.heappush(self.right_min_heap, max_left)

        # 如果小堆元素比大堆多，调整平衡
        if len(self.left_max_heap) < len(self.right_min_heap):
            min_right = heapq.heappop(self.right_min_heap)
            heapq.heappush(self.left_max_heap, -min_right)

    def findMedian(self) -> float:
        """ 获取当前数据流的中位数 """
        if len(self.left_max_heap) > len(self.right_min_heap):
            return -self.left_max_heap[0]  # 最大堆的堆顶是中位数
        return (-self.left_max_heap[0] + self.right_min_heap[0]) / 2.0  # 堆顶平均数是中位数


if __name__ == "__main__":
    median = MedianFinder()
    test_data = [5, 15, 1, 3]

    for num in test_data:
        median.addNum(num)
        print(f"插入 {num} 后的中位数: {median.findMedian()}")
