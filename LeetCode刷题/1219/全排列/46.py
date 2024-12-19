def permute(nums):
    def backtrack(path, remaining):
        if not remaining:  # 基准条件：当没有剩余元素时，加入当前排列
            result.append(path)
            return

        for i in range(len(remaining)):
            # 选择当前元素并进行递归
            backtrack(path + [remaining[i]], remaining[:i] + remaining[i+1:])

    result = []
    backtrack([], nums)
    return result
