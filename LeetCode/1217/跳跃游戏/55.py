def canJump(nums):
    farthest = 0
    for i in range(len(nums)):
        if i > farthest:  # 如果当前索引超出了能够到达的最远位置，返回 False
            return False
        farthest = max(farthest, i + nums[i])  # 更新最远可达位置
        if farthest >= len(nums) - 1:  # 如果最远可达位置已经到达或超过最后一个位置
            return True
    return False
