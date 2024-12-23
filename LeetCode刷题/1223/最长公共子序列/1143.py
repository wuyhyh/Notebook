def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)

    # 初始化 dp 数组，dp[i][j] 表示 text1[0...i-1] 和 text2[0...j-1] 的 LCS 长度
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 填充 dp 数组
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1  # 当前字符匹配，LCS 长度加 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # 当前字符不匹配，取最大值

    # 返回最终的 LCS 长度
    return dp[m][n]
