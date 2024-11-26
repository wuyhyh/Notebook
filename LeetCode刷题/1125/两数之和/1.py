def two_sum(nums, target):
    # 创建一个哈希表来存储数值和它们的索引
    num_dict = {}

    # 遍历数组中的每个元素
    for i, num in enumerate(nums):
        # 计算差值，看看是否已经存在于哈希表中
        complement = target - num
        if complement in num_dict:
            # 如果找到匹配的元素，返回它们的索引
            return [num_dict[complement], i]
        # 否则将当前元素存入哈希表
        num_dict[num] = i
    # 如果没有找到符合条件的解，返回空列表
    return []

# 示例用法
nums = [2, 7, 11, 15]
target = 9
result = two_sum(nums, target)

# 输出结果
if result:
    print(result)  # 输出: [0, 1]
else:
    print("No solution found.")
