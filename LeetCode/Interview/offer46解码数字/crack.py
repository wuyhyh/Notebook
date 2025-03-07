class Solution:
    def crack_num(self, ciphertext: int) -> int:
        # 计算加密数字ciphertext有多少种解法
        # 将数字转换为字符串
        s = str(ciphertext)

        # 记忆已经计算过的结果，避免重复计算
        memo = {}

        # 递归函数，从index开始的子串有多少种解法
        def dfs(index):
            if index == len(s):  # 递归终止条件，到达了字符串末尾
                return 1
            if index in memo:  # 已经计算过的方案，直接返回存储的结果
                return memo[index]

            curr_count = 0
            # 方式1，取单个数字解码
            if 0 <= int(s[index]) <= 25:
                curr_count += dfs(index + 1)
            # 方式2，取2个数字解码
            if index + 1 < len(s):  # 避免越界
                two_digit = int(s[index:index + 2])
                if 10 <= two_digit <= 25:
                    curr_count += dfs(index + 2)

            memo[index] = curr_count  # 记忆结果
            return curr_count

        # 外层函数
        return dfs(0)


if __name__ == '__main__':
    s = Solution()
    print(s.crack_num(216612))
    print(s.crack_num(25))
    print(s.crack_num(0))
    print(s.crack_num(101))
    print(s.crack_num(506))
