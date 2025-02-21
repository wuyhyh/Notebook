### **LeetCode 第394题 - 字符串解码 (Decode String)**

#### **题目描述**

给定一个经过编码的字符串 `s`，返回它解码后的字符串。

编码规则：
- `k[encoded_string]` 代表着字符串 `encoded_string` 被重复 `k` 次。
- `k` 是一个正整数，`encoded_string` 可能包含字母，数字或其他字符。

#### **示例**

示例 1:
```python
s = "3[a]2[bc]"
print(decodeString(s))  # 输出 "aaabcbc"
```

示例 2:
```python
s = "3[a2[c]]"
print(decodeString(s))  # 输出 "accaccacc"
```

示例 3:
```python
s = "2[abc]3[cd]ef"
print(decodeString(s))  # 输出 "abcabccdcdcdef"
```

#### **思路分析**

该问题的核心是如何解码具有嵌套结构的字符串。为了解决这个问题，我们可以使用 **栈**（Stack）来处理字符串的解码。

#### **解题步骤**：
1. **遍历字符串**：
    - 遇到数字时，表示当前重复的次数，将其累加直到完整读取数字。
    - 遇到左括号 `[` 时，表示进入一个新的编码块，需要将当前的重复次数和之前的解码结果都推入栈中。
    - 遇到右括号 `]` 时，表示当前编码块结束，弹出栈顶的重复次数和之前的字符串，并进行解码（即重复当前编码块中的字符串）。
    - 遇到字母时，直接加入当前构建的字符串。

2. **处理嵌套情况**：
    - 当遇到一个左括号 `[`，将当前的数字（重复次数）和当前的构建字符串推入栈中，并清空当前构建字符串。
    - 当遇到右括号 `]`，将当前构建的字符串重复并合并到栈中的字符串上。

3. **栈的应用**：
    - 使用栈来保存每一层的解码信息（重复次数和已经解码的字符串），确保解码的顺序是从内到外的。

### **代码实现**

```python
def decodeString(s: str) -> str:
    stack = []  # 用来存储当前解码的状态（重复次数和解码字符串）
    current_string = ""  # 当前构建的字符串
    current_num = 0  # 当前的重复次数
    
    for char in s:
        if char.isdigit():
            # 构造重复次数，可能有多位数字
            current_num = current_num * 10 + int(char)
        elif char == '[':
            # 遇到左括号时，将当前重复次数和构建的字符串入栈
            stack.append((current_num, current_string))
            current_num = 0  # 重置重复次数
            current_string = ""  # 重置当前字符串
        elif char == ']':
            # 遇到右括号时，弹出栈顶元素并解码
            last_num, last_string = stack.pop()
            current_string = last_string + current_string * last_num
        else:
            # 遇到字母时，添加到当前构建的字符串
            current_string += char
    
    return current_string
```

### **代码解析**

1. **`stack`**：用于存储当前处理过程中的重复次数和构建的字符串。
    - 每当遇到左括号 `[` 时，我们将当前的 `current_num` 和 `current_string` 压入栈中。
    - 每当遇到右括号 `]` 时，我们从栈中弹出重复次数和之前的字符串，进行解码。

2. **`current_string`**：用于存储当前的解码字符串。
    - 在遍历过程中，不断构建当前解码的部分字符串。

3. **`current_num`**：用于存储当前数字（即重复的次数）。
    - 如果遇到一个数字，我们会更新 `current_num`，直到遇到左括号 `[`。

4. **遍历字符串**：
    - 如果字符是数字，更新 `current_num`。
    - 如果字符是左括号 `[`，将 `current_num` 和 `current_string` 入栈，重置为新的状态。
    - 如果字符是右括号 `]`，从栈中弹出并进行解码，将解码结果保存在 `current_string` 中。
    - 如果字符是字母，直接添加到 `current_string`。

### **时间复杂度**

- **时间复杂度**：`O(n)`，其中 `n` 是字符串的长度。我们只需要遍历字符串一次，并进行常数时间的栈操作。
- **空间复杂度**：`O(n)`，栈的最大深度为字符串的嵌套层数，最坏情况下所有字符都是数字或括号，需要 `O(n)` 的空间。

### **示例**

#### 示例 1：

```python
s = "3[a]2[bc]"
print(decodeString(s))  # 输出 "aaabcbc"
```

**解释**：
- `3[a]` 解码为 `aaa`。
- `2[bc]` 解码为 `bcbc`。
- 最终拼接结果为 `"aaabcbc"`。

#### 示例 2：

```python
s = "3[a2[c]]"
print(decodeString(s))  # 输出 "accaccacc"
```

**解释**：
- `a2[c]` 解码为 `acc`。
- `3[a2[c]]` 解码为 `accaccacc`。

#### 示例 3：

```python
s = "2[abc]3[cd]ef"
print(decodeString(s))  # 输出 "abcabccdcdcdef"
```

**解释**：
- `2[abc]` 解码为 `abcabc`。
- `3[cd]` 解码为 `cdcdcd`。
- 最终拼接结果为 `"abcabccdcdcdef"`。

### **总结**

- 使用栈来处理括号嵌套问题，栈能够帮助我们处理不同层级的解码过程。
- 时间复杂度是 `O(n)`，每个字符只遍历一次，栈操作是常数时间。
- 通过栈的帮助，能够简洁地处理复杂的嵌套结构。
