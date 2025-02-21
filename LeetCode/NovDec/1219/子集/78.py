def subsets(nums):
    def backtrack(start, path):
        # 将当前子集加入结果
        result.append(path[:])
        # 遍历剩余元素
        for i in range(start, len(nums)):
            path.append(nums[i])  # 选择当前元素
            backtrack(i + 1, path)  # 递归调用
            path.pop()  # 回溯，撤销选择

    result = []
    backtrack(0, [])
    return result
