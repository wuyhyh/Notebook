# LeetCode 第49题：字母异位词分组

### 问题描述

你提到想学习LeetCode第49题，这个题目要求我们将一组字符串按照字母异位词进行分组。字母异位词是指由相同字符组成的不同排列，例如“eat”和“tea”是字母异位词。

### 代码实现

以下是字母异位词分组的 Python 解法：

```python
from collections import defaultdict

def group_anagrams(strs):
    # 创建一个字典来存储字母异位词组
    anagrams = defaultdict(list)
    
    # 遍历字符串列表
    for s in strs:
        # 将字符串排序，作为字典的键
        sorted_str = ''.join(sorted(s))
        # 将原始字符串加入对应的键的列表中
        anagrams[sorted_str].append(s)
    
    # 返回字典中所有值的列表
    return list(anagrams.values())

# 示例用法
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
result = group_anagrams(strs)

# 输出结果
print(result)  # 输出: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

### 问题和讲解

**1. 为什么使用 `defaultdict`？**

在代码中，`from collections import defaultdict` 导入了 `defaultdict`，这是 Python 中字典的一个子类。它的好处是，当你访问一个不存在的键时，它会自动为该键生成一个默认值。`defaultdict(list)` 创建了一个字典，其中默认值是空列表，这样就可以直接将元素加入列表中，而无需先检查键是否存在。

**2. 为什么 `defaultdict(list)` 中有一个 `list` 参数？**

`defaultdict(list)` 中的 `list` 参数表示默认值的类型。当访问字典中不存在的键时，它会自动生成一个空列表 `[]`，这样你可以直接使用 `append` 方法将元素添加进去，避免了手动处理键不存在时可能抛出的错误。

**3. `sorted_str = ''.join(sorted(s))` 的作用是什么？**

`sorted_str = ''.join(sorted(s))` 的作用是将字符串 `s` 中的字符按字母顺序进行排序，并将它们重新组合成一个新的字符串。

- `sorted(s)` 返回字符串 `s` 中字符排序后的列表。例如，对于字符串 `"eat"`，`sorted(s)` 返回 `['a', 'e', 't']`。
- `''.join(sorted(s))` 会将这个列表中的字符重新组合成一个字符串，例如 `''.join(['a', 'e', 't'])` 会得到 `"aet"`。

这样，具有相同字符的不同字符串（如 `"eat"` 和 `"tea"`）在排序后得到相同的字符串（`"aet"`），从而可以作为字典的键来分组字母异位词。

**4. `list(anagrams.values())` 的作用是什么？**

`list(anagrams.values())` 的作用是将 `anagrams` 字典中所有的值（即每个字母异位词的列表）提取出来，并将它们转换为一个列表对象。

- `anagrams` 是一个 `defaultdict`，其中的值是按排序后的字符串键组织起来的字母异位词列表。
- `anagrams.values()` 返回包含所有这些列表的视图对象。
- `list(anagrams.values())` 将该视图转换为一个实际的列表，返回所有字母异位词的分组。

例如，假设 `anagrams` 的内容是 `{ "aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"], "abt": ["bat"] }`，那么 `list(anagrams.values())` 会返回 `[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]`。

这种转换可以让输出符合题目要求，即返回所有字母异位词的分组。

