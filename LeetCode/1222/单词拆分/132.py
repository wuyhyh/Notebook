def wordBreak(s, wordDict):
    wordSet = set(wordDict)  # 将字典转换为集合，查找更高效
    n = len(s)

    # dp[i] 表示 s[0:i] 是否能由字典中的单词组成
    dp = [False] * (n + 1)
    dp[0] = True  # 空字符串可以拆分

    # 遍历所有可能的子串
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in wordSet:
                dp[i] = True
                break

    return dp[n]
