LeetCode 第 238 题：**除自身以外数组的乘积（Product of Array Except Self）**，是一个经典的数组问题，要求在不使用除法的情况下，计算一个数组中每个元素的“除自身以外的乘积”。换句话说，对于给定数组 `nums`，我们需要输出一个新的数组 `output`，其中 `output[i]` 为数组中所有元素乘积的结果，除了 `nums[i]` 之外的所有元素。

### 问题描述

给定一个长度为 `n` 的整数数组 `nums`，你需要返回一个同样长度的数组 `output`，满足：
- `output[i] = product(nums[0]...nums[i-1], nums[i+1]...nums[n-1])`
- 不能使用除法（即不能用 `/` 运算符）。

### 示例

**输入:**
```plaintext
nums = [1, 2, 3, 4]
```

**输出:**
```plaintext
[24, 12, 8, 6]
```

**解释:**
- `output[0] = 2 * 3 * 4 = 24`
- `output[1] = 1 * 3 * 4 = 12`
- `output[2] = 1 * 2 * 4 = 8`
- `output[3] = 1 * 2 * 3 = 6`

### 思路分析

我们不能直接使用除法，但我们可以通过 **两次遍历** 来实现这个功能：

1. **前缀积（prefix product）**：
    - 计算从左到右的所有元素的累积乘积。
    - 我们可以利用一个数组 `left` 来保存当前元素之前的所有元素的乘积。

2. **后缀积（suffix product）**：
    - 计算从右到左的所有元素的累积乘积。
    - 我们可以使用一个变量 `right` 来保存当前元素之后的所有元素的乘积。

3. **结合前缀积和后缀积**：
    - 最终的结果是前缀积和后缀积的乘积，即：`output[i] = left[i] * right[i]`。

4. **空间优化**：
    - 由于 `left` 和 `right` 可以在 `output` 数组中完成，因此我们可以只使用一个数组来保存结果，并通过两次遍历来计算。

---

### 解法

1. **初始化**：
    - 用一个数组 `output` 来存储结果，初始化为 `output[i] = 1`。
    - 第一次遍历用来计算前缀积。
    - 第二次遍历用来计算后缀积，并将其与前缀积结合，得到最终结果。

---

### 代码实现

```python
def productExceptSelf(nums):
    n = len(nums)
    
    # 初始化输出数组
    output = [1] * n

    # 计算前缀积并存储到 output 数组中
    prefix_product = 1
    for i in range(n):
        output[i] = prefix_product
        prefix_product *= nums[i]

    # 计算后缀积并与前缀积结合
    suffix_product = 1
    for i in range(n-1, -1, -1):
        output[i] *= suffix_product
        suffix_product *= nums[i]

    return output
```

### 代码解释

1. **初始化输出数组**：
   ```python
   output = [1] * n
   ```
    - 创建一个大小为 `n` 的数组 `output`，并初始化所有元素为 `1`。

2. **计算前缀积**：
   ```python
   prefix_product = 1
   for i in range(n):
       output[i] = prefix_product
       prefix_product *= nums[i]
   ```
    - 我们首先计算数组中每个位置左侧（包括当前位）所有元素的乘积，存储在 `output` 中。`prefix_product` 变量用于存储到当前位置为止的乘积。
    - 在遍历过程中，`output[i]` 存储的是 `nums[0] * nums[1] * ... * nums[i-1]` 的乘积。

3. **计算后缀积并更新输出**：
   ```python
   suffix_product = 1
   for i in range(n-1, -1, -1):
       output[i] *= suffix_product
       suffix_product *= nums[i]
   ```
    - 然后从右到左遍历数组，计算每个位置右侧（包括当前位）所有元素的乘积，并将结果与 `output[i]` 相乘，得到最终的乘积。
    - `suffix_product` 变量用于存储从当前位置到数组末尾的乘积。

4. **返回最终结果**：
    - 遍历完成后，`output` 数组即包含了每个元素以外的所有元素的乘积。

---

### 例子分析

假设输入 `nums = [1, 2, 3, 4]`，我们来看下每一步的过程。

1. **初始化输出数组**：
   ```plaintext
   output = [1, 1, 1, 1]
   ```

2. **计算前缀积**：
    - `prefix_product = 1`，遍历数组：
        - 第 1 步：`output[0] = 1`，`prefix_product = 1 * 1 = 1`
        - 第 2 步：`output[1] = 1`，`prefix_product = 1 * 2 = 2`
        - 第 3 步：`output[2] = 2`，`prefix_product = 2 * 3 = 6`
        - 第 4 步：`output[3] = 6`，`prefix_product = 6 * 4 = 24`
    - 经过这一步后，`output` 数组变为：
   ```plaintext
   output = [1, 1, 2, 6]
   ```

3. **计算后缀积并更新输出**：
    - `suffix_product = 1`，从右往左遍历数组：
        - 第 1 步：`output[3] = 6 * 1 = 6`，`suffix_product = 1 * 4 = 4`
        - 第 2 步：`output[2] = 2 * 4 = 8`，`suffix_product = 4 * 3 = 12`
        - 第 3 步：`output[1] = 1 * 12 = 12`，`suffix_product = 12 * 2 = 24`
        - 第 4 步：`output[0] = 1 * 24 = 24`，`suffix_product = 24 * 1 = 24`
    - 最终的 `output` 数组变为：
   ```plaintext
   output = [24, 12, 8, 6]
   ```

### 时间复杂度与空间复杂度

- **时间复杂度**：
    - 计算前缀积和后缀积各需要一次遍历数组，因此时间复杂度是 `O(n)`，其中 `n` 是数组的长度。

- **空间复杂度**：
    - 我们只用了一个额外的数组 `output` 来存储结果，因此空间复杂度是 `O(n)`。如果我们不使用额外的空间，空间复杂度就可以优化为 `O(1)`（使用原数组进行修改）。

---

### 总结

1. **问题要求**：我们需要计算每个元素以外所有元素的乘积，而不能使用除法。
2. **解法**：通过两次遍历：一次计算前缀积，一次计算后缀积，并将两者结合来得到结果。
3. **时间复杂度**：`O(n)`，其中 `n` 是数组的长度。
4. **空间复杂度**：`O(n)`，如果优化空间，使用原数组则是 `O(1)`。

如果你有任何问题，或者对某个部分不理解，随时告诉我！