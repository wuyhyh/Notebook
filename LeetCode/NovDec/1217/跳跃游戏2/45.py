def jump(nums):
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):  # 不需要跳到最后一个位置
        farthest = max(farthest, i + nums[i])  # 更新能到达的最远位置
        if i == current_end:  # 到达当前跳跃范围的最后一个位置
            jumps += 1  # 增加跳跃次数
            current_end = farthest  # 更新当前跳跃范围
            if current_end >= len(nums) - 1:  # 如果已经到达或超过最后一个位置
                break
    return jumps
