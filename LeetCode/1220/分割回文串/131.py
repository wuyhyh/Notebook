def partition(s):
    result = []

    # 判断一个字符串是否为回文串
    def is_palindrome(sub):
        return sub == sub[::-1]

    # 回溯函数，cur_list 存储当前的分割方案
    def backtrack(start, cur_list):
        # 如果起始位置已经达到字符串的末尾，说明一组分割完成
        if start == len(s):
            result.append(cur_list[:])  # 将当前分割方案加入结果
            return

        # 从 start 开始遍历
        for end in range(start + 1, len(s) + 1):
            # 提取当前子串
            substring = s[start:end]
            if is_palindrome(substring):
                cur_list.append(substring)  # 将回文子串加入当前分割方案
                backtrack(end, cur_list)    # 递归处理剩余部分
                cur_list.pop()  # 回溯，移除当前子串

    # 从位置 0 开始回溯
    backtrack(0, [])
    return result
