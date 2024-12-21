def rob(nums):
    if not nums:
        return 0
    elif len(nums) == 1:
        return nums[0]

    # 初始化 dp 数组
    dp = [0] * len(nums)
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])

    # 填充 dp 数组
    for i in range(2, len(nums)):
        dp[i] = max(dp[i - 1], dp[i - 2] + nums[i])

    return dp[-1]
