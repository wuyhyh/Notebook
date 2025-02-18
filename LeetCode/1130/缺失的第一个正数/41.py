def firstMissingPositive(nums):
    n = len(nums)

    # 第一步：将不在 [1, n] 范围内的数字置为 n+1
    for i in range(n):
        if nums[i] <= 0 or nums[i] > n:
            nums[i] = n + 1

    # 第二步：将每个数字放到它应该在的位置
    for i in range(n):
        val = abs(nums[i])
        if 1 <= val <= n:
            if nums[val - 1] > 0:  # 防止重复标记
                nums[val - 1] = -abs(nums[val - 1])  # 将该位置的数字标记为负数

    # 第三步：找到第一个位置 i，满足 nums[i] > 0，返回 i + 1
    for i in range(n):
        if nums[i] > 0:
            return i + 1

    # 如果所有位置都已经符合条件，返回 n + 1
    return n + 1
