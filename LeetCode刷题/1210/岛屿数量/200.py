class Solution(object):
    def numIslands(self, grid):
        """
        :type grid: List[List[str]]
        :rtype: int
        """
        # 边界检查
        if not grid:
            return 0

        # 行数和列数
        m, n = len(grid), len(grid[0])

        # DFS 函数，标记连通区域
        def dfs(i, j):
            # 如果越界或当前位置是水域，则返回
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == '0':
                return
            # 将当前陆地标记为已访问
            grid[i][j] = '0'
            # 递归访问上下左右
            dfs(i - 1, j)  # 上
            dfs(i + 1, j)  # 下
            dfs(i, j - 1)  # 左
            dfs(i, j + 1)  # 右

        # 岛屿数量
        island_count = 0

        # 遍历整个网格
        for i in range(m):
            for j in range(n):
                # 遇到陆地 '1'，表示找到了一个新的岛屿
                if grid[i][j] == '1':
                    island_count += 1
                    # 通过 DFS 将岛屿的所有陆地标记为已访问
                    dfs(i, j)

        return island_count
