### **LeetCode 第208题 - 实现 Trie（前缀树）**

#### **题目描述**
实现一个前缀树（Trie），支持以下三种操作：
1. `insert(word)`：将字符串 `word` 插入前缀树。
2. `search(word)`：如果字符串 `word` 在前缀树中完整匹配，则返回 `True`；否则返回 `False`。
3. `startsWith(prefix)`：如果前缀树中存在以 `prefix` 开头的字符串，则返回 `True`；否则返回 `False`。

---

### **解题思路**

前缀树（Trie）是一种树形数据结构，适合高效地存储和查找字符串前缀。以下是实现的关键点：

1. **节点结构**：
    - 每个节点存储一个 `children` 字典，用于存储该节点的子节点。
    - 一个布尔值 `is_end`，表示是否有单词以该节点结尾。

2. **基本操作**：
    - **插入操作（`insert`）**：
        - 从根节点出发，根据 `word` 的每个字符逐步向下插入，如果节点不存在则创建。
        - 最后一个字符的节点标记为 `is_end = True`。
    - **查找操作（`search` 和 `startsWith`）**：
        - 从根节点开始，根据字符串逐步向下查找。
        - 如果中途某个字符不存在，直接返回 `False`。
        - 对于 `search`，还需检查最后一个节点的 `is_end` 是否为 `True`。

3. **时间复杂度**：
    - **插入和查找**的时间复杂度为 \(O(m)\)，其中 \(m\) 是字符串的长度。

---

### **代码实现**

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # 存储子节点
        self.is_end = False  # 表示是否是一个单词的结尾

class Trie:
    def __init__(self):
        self.root = TrieNode()  # 初始化根节点

    def insert(self, word):
        """
        插入一个单词到前缀树中
        :type word: str
        :rtype: None
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True  # 标记单词结尾

    def search(self, word):
        """
        搜索一个单词是否存在于前缀树中
        :type word: str
        :rtype: bool
        """
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):
        """
        判断是否存在以 prefix 为前缀的单词
        :type prefix: str
        :rtype: bool
        """
        return self._find_node(prefix) is not None

    def _find_node(self, prefix):
        """
        辅助函数：根据前缀返回最后一个节点
        :type prefix: str
        :rtype: TrieNode
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
```

---

### **方法解析**

#### 1. **`insert` 方法**：
- **步骤**：
    1. 从根节点开始，遍历字符串的每个字符。
    2. 如果字符不存在于当前节点的 `children` 中，则创建一个新的子节点。
    3. 移动到当前字符对应的子节点。
    4. 遍历结束后，标记最后一个节点为单词的结尾（`is_end = True`）。

#### 2. **`search` 方法**：
- **步骤**：
    1. 调用 `_find_node` 辅助函数查找字符串对应的最后一个节点。
    2. 如果节点存在且 `is_end` 为 `True`，返回 `True`；否则返回 `False`。

#### 3. **`startsWith` 方法**：
- **步骤**：
    1. 调用 `_find_node` 辅助函数查找前缀对应的最后一个节点。
    2. 如果节点存在，返回 `True`；否则返回 `False`。

#### 4. **`_find_node` 辅助函数**：
- **功能**：沿着字符串路径查找对应的最后一个节点。如果中途遇到不存在的字符，直接返回 `None`。

---

### **复杂度分析**

1. **时间复杂度**：
    - **`insert`**：每次插入需要遍历字符串的每个字符，复杂度为 \(O(m)\)，其中 \(m\) 是字符串的长度。
    - **`search` 和 `startsWith`**：类似地，需要遍历字符串的每个字符，复杂度为 \(O(m)\)。

2. **空间复杂度**：
    - 每次插入操作可能需要创建新的节点，最坏情况下需要 \(O(n \times m)\) 的空间，其中 \(n\) 是单词数量，\(m\) 是单词的平均长度。

---

### **示例测试**

#### 示例 1：
```python
# 初始化 Trie
trie = Trie()
trie.insert("apple")
print(trie.search("apple"))  # 输出 True
print(trie.search("app"))    # 输出 False
print(trie.startsWith("app")) # 输出 True
trie.insert("app")
print(trie.search("app"))    # 输出 True
```

---

### **总结**
- **前缀树（Trie）** 是解决字符串前缀相关问题的有效数据结构，能够高效地完成插入和查找操作。
- 本题关键在于理解 Trie 的结构及其操作的基本流程。
- 该实现通过邻接字典和布尔值标记实现节点的功能，代码简洁且高效，适合应用于大规模的字符串前缀匹配问题。
