def canPartition(nums):
    total_sum = sum(nums)

    # 如果总和是奇数，无法分成两个相等的子集
    if total_sum % 2 != 0:
        return False

    # 目标和
    target = total_sum // 2

    # 创建动态规划数组，初始化 dp[0] = True，表示和为 0 可以通过选择空集来实现
    dp = [False] * (target + 1)
    dp[0] = True

    # 遍历每个数字
    for num in nums:
        # 逆序更新 dp 数组，防止重复使用当前数字
        for i in range(target, num - 1, -1):
            dp[i] = dp[i] or dp[i - num]

    # 如果 dp[target] 为 True，表示存在和为 target 的子集
    return dp[target]
