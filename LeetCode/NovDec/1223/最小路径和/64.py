def minPathSum(grid):
    if not grid:
        return 0

    m, n = len(grid), len(grid[0])

    # 初始化 dp 数组，dp[i][j] 代表从 (0,0) 到 (i,j) 的最小路径和
    dp = [[0] * n for _ in range(m)]

    # 初始化左上角
    dp[0][0] = grid[0][0]

    # 初始化第一列
    for i in range(1, m):
        dp[i][0] = dp[i-1][0] + grid[i][0]

    # 初始化第一行
    for j in range(1, n):
        dp[0][j] = dp[0][j-1] + grid[0][j]

    # 填充 dp 数组
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])

    # 返回右下角的最小路径和
    return dp[m-1][n-1]
