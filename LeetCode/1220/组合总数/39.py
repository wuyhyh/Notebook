def combinationSum(candidates, target):
    result = []

    def backtrack(start, target, path):
        if target == 0:
            result.append(path[:])  # 当前组合有效，加入结果
            return
        if target < 0:
            return  # 当前组合无效，结束递归

        # 从当前位置开始，尝试每个候选数字
        for i in range(start, len(candidates)):
            path.append(candidates[i])  # 选择当前数字
            backtrack(i, target - candidates[i], path)  # 递归调用，注意不改变起始位置 i
            path.pop()  # 回溯，撤销选择

    backtrack(0, target, [])
    return result
