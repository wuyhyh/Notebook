from collections import deque

def maxSlidingWindow(nums, k):
    # 边界条件：如果数组为空，直接返回空列表
    if not nums:
        return []

    # 双端队列，保存的是元素的索引，保证队列按降序排列
    dq = deque()
    result = []

    for i in range(len(nums)):
        # 移除队首元素，如果它已经不在当前窗口内
        if dq and dq[0] < i - k + 1:
            dq.popleft()

        # 移除队尾的元素，直到队尾的元素大于当前元素
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        # 将当前元素的索引加入队列
        dq.append(i)

        # 当索引达到 k - 1 时，开始记录窗口最大值
        if i >= k - 1:
            result.append(nums[dq[0]])  # 队首元素是当前窗口的最大值

    return result