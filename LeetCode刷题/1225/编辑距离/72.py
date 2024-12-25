def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)

    # 创建 dp 数组，dp[i][j] 表示 word1 的前 i 个字符转化为 word2 的前 j 个字符的最小编辑距离
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 初始化第一列和第一行
    for i in range(m + 1):
        dp[i][0] = i  # word1 的前 i 个字符转化为空字符串需要 i 次删除
    for j in range(n + 1):
        dp[0][j] = j  # 空字符串转化为 word2 的前 j 个字符需要 j 次插入

    # 填充 dp 数组
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # 如果字符相同，不需要操作
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # 删除操作
                    dp[i][j - 1] + 1,  # 插入操作
                    dp[i - 1][j - 1] + 1  # 替换操作
                )

    # 最终结果是将 word1 转换为 word2 的编辑距离
    return dp[m][n]
