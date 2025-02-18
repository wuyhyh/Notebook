import heapq

class MedianFinder:
    def __init__(self):
        # 最大堆：存储较小的一半元素 (使用负数模拟最大堆)
        self.left = []  # 最大堆
        # 最小堆：存储较大的一半元素
        self.right = []  # 最小堆

    def addNum(self, num: int) -> None:
        # 总是将新元素添加到最大堆（left）
        heapq.heappush(self.left, -num)

        # 将最大堆的最大元素（注意是负数）移到最小堆（right）
        heapq.heappush(self.right, -heapq.heappop(self.left))

        # 保证右边堆的大小要么等于左边堆，要么比左边堆多一个元素
        if len(self.left) < len(self.right):
            heapq.heappush(self.left, -heapq.heappop(self.right))

    def findMedian(self) -> float:
        # 如果左堆多一个元素，则中位数就是左堆的堆顶元素
        if len(self.left) > len(self.right):
            return -self.left[0]
        # 否则，中位数是左右堆的堆顶元素的平均值
        return (-self.left[0] + self.right[0]) / 2.0
