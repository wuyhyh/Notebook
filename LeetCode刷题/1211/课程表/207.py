class Solution:
    def canFinish(self, numCourses, prerequisites):
        """
        :type numCourses: int
        :type prerequisites: List[List[int]]
        :rtype: bool
        """
        # 构建图
        graph = defaultdict(list)
        for course, pre in prerequisites:
            graph[pre].append(course)

        # 访问状态：0 = 未访问，1 = 访问中，2 = 已访问
        visited = [0] * numCourses

        def dfs(course):
            if visited[course] == 1:  # 当前节点在访问中，说明存在环
                return False
            if visited[course] == 2:  # 当前节点已经访问过，无需重复检查
                return True

            # 标记当前节点为访问中
            visited[course] = 1

            # 递归访问邻接节点
            for next_course in graph[course]:
                if not dfs(next_course):
                    return False

            # 标记当前节点为已访问
            visited[course] = 2
            return True

        # 遍历所有节点，检查是否有环
        for i in range(numCourses):
            if not dfs(i):
                return False

        return True
