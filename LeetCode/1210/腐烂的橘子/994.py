from collections import deque

class Solution(object):
    def orangesRotting(self, grid):
        """
        :type grid: List[List[int]]
        :rtype: int
        """
        # 如果网格为空，返回0
        if not grid:
            return 0

        # 初始化队列，加入所有腐烂橘子的坐标
        queue = deque()
        fresh_count = 0
        rows, cols = len(grid), len(grid[0])

        # 将所有腐烂橘子加入队列，统计新鲜橘子的数量
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 2:  # 腐烂橘子
                    queue.append((r, c))
                elif grid[r][c] == 1:  # 新鲜橘子
                    fresh_count += 1

        # 如果没有新鲜橘子，直接返回0
        if fresh_count == 0:
            return 0

        # BFS过程，模拟腐烂的扩散
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        minutes = 0

        # 开始BFS
        while queue:
            size = len(queue)
            # 记录当前层次（每分钟）腐烂橘子的扩展
            for _ in range(size):
                r, c = queue.popleft()
                # 尝试四个方向扩散
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    # 判断新的位置是否合法且为新鲜橘子
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        grid[nr][nc] = 2  # 将新鲜橘子变为腐烂
                        fresh_count -= 1
                        queue.append((nr, nc))

            # 只有当当前层级（即一轮腐烂扩展）结束后才增加分钟数
            if queue:  # 如果队列中还有腐烂橘子
                minutes += 1

        # 如果还有新鲜橘子未腐烂，返回-1
        return minutes if fresh_count == 0 else -1
