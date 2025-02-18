### **LeetCode 第207题 - 课程表（Course Schedule）**

#### **题目描述**
你需要判断是否能够完成所有课程的学习。这些课程用从 `0` 到 `numCourses-1` 的数字表示。给定课程的先修条件（Prerequisites），用一个二维数组 `prerequisites` 表示，其中 `prerequisites[i] = [a, b]` 表示要学习课程 `a`，你需要先完成课程 `b`。

返回 `True` 如果能够完成所有课程，否则返回 `False`。

---

### **解题思路**

这是一个**有向图的拓扑排序问题**，目标是判断图中是否存在**环**。
1. **图的表示**：
    - 将课程和先修关系用**有向图**表示。
    - 使用邻接表构建图，`graph[b]` 表示课程 `b` 是哪些课程的先修课程。

2. **检测是否有环**：
    - 如果图中存在环，则不能完成所有课程，返回 `False`。
    - 如果图中无环，则可以完成所有课程，返回 `True`。

3. **解决方法**：
    - **入度法（Kahn's Algorithm）**：
        - 记录每个节点的入度（即需要先修课程的数量）。
        - 逐步移除入度为 `0` 的节点，并更新其邻接节点的入度。
        - 如果最终所有节点都被移除，则无环；否则有环。
    - **深度优先搜索（DFS）**：
        - 检测图中的环。通过维护一个访问状态数组（未访问、访问中、已访问），检查是否存在回到“访问中”节点的情况。

---

### **方法一：入度法（BFS 拓扑排序）**

#### **代码实现**

```python
from collections import deque, defaultdict

class Solution:
    def canFinish(self, numCourses, prerequisites):
        """
        :type numCourses: int
        :type prerequisites: List[List[int]]
        :rtype: bool
        """
        # 构建图和入度表
        graph = defaultdict(list)
        in_degree = [0] * numCourses
        
        for course, pre in prerequisites:
            graph[pre].append(course)
            in_degree[course] += 1
        
        # 将入度为0的节点加入队列
        queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
        visited = 0  # 记录已访问的节点数
        
        while queue:
            course = queue.popleft()
            visited += 1  # 访问节点
            
            # 遍历当前节点的邻接节点
            for next_course in graph[course]:
                in_degree[next_course] -= 1  # 入度减1
                if in_degree[next_course] == 0:  # 入度为0时加入队列
                    queue.append(next_course)
        
        # 如果访问的节点数等于课程数，则无环
        return visited == numCourses
```

#### **思路解析**
1. **图的构建**：
    - 使用邻接表表示有向图，`graph[b]` 是一个列表，表示课程 `b` 的所有后续课程。
    - 同时记录每个课程的入度，`in_degree[i]` 表示需要完成多少先修课程才能学习课程 `i`。

2. **拓扑排序**：
    - 将所有入度为 `0` 的节点加入队列，表示这些课程可以直接学习。
    - 每次从队列中取出一个课程，将其从图中移除，并将它指向的课程的入度减 1。
    - 如果某个课程的入度变为 `0`，将其加入队列。
    - 最终，如果所有课程都被访问（`visited == numCourses`），说明图中无环。

3. **判断条件**：
    - 如果最终访问的节点数等于总课程数，返回 `True`；否则返回 `False`。

---

### **方法二：深度优先搜索（DFS 检测环）**

#### **代码实现**

```python
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
```

#### **思路解析**
1. **图的构建**：
    - 使用邻接表表示有向图，`graph[b]` 表示课程 `b` 的所有后续课程。

2. **环检测**：
    - 使用一个 `visited` 数组记录每个节点的访问状态：
        - `0`：未访问。
        - `1`：访问中。
        - `2`：已访问。
    - 如果在 DFS 中回到一个正在访问的节点（`visited[course] == 1`），说明存在环。

3. **递归逻辑**：
    - 遍历节点的所有邻接节点，如果某条路径上存在环，返回 `False`。
    - 如果当前路径无环，标记节点为已访问（`visited[course] = 2`）。

4. **判断条件**：
    - 如果图中存在环，返回 `False`；否则返回 `True`。

---

### **时间复杂度与空间复杂度**

#### **时间复杂度**：
- 图的构建需要 \(O(E)\)，其中 \(E\) 是先修课程的数量。
- BFS 或 DFS 需要遍历每个节点和边，总复杂度为 \(O(V + E)\)，其中 \(V\) 是课程数量。

#### **空间复杂度**：
- **BFS**：需要额外的队列存储入度为 `0` 的节点，空间复杂度为 \(O(V)\)。
- **DFS**：需要递归调用栈，最坏情况下深度为 \(O(V)\)。

---

### **示例测试**

#### 示例 1：
```python
numCourses = 2
prerequisites = [[1, 0]]
```
输出：
```python
True
```
解释：可以学习课程 `0`，然后学习课程 `1`。

#### 示例 2：
```python
numCourses = 2
prerequisites = [[1, 0], [0, 1]]
```
输出：
```python
False
```
解释：课程 `1` 依赖课程 `0`，而课程 `0` 依赖课程 `1`，形成环，无法完成课程。

---

### **总结**
- **拓扑排序法（BFS）**：通过入度表判断课程之间的依赖关系，逐层消除入度为 `0` 的节点，适合检查是否存在环。
- **深度优先搜索（DFS）**：通过递归判断路径中是否存在环，简单直观。
- 两种方法均可高效解决本题，时间复杂度为 \(O(V + E)\)，适用于大规模图问题。
