def lengthOfLIS(nums):
    if not nums:
        return 0

    n = len(nums)
    dp = [1] * n  # 初始化 dp 数组，dp[i] 表示以 nums[i] 为结尾的最长递增子序列的长度

    for i in range(1, n):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)  # 返回最长递增子序列的长度
