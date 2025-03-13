from collections import Counter
from importlib.metadata import requires


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not s or not t:
            return ""

        # 记录t中每个字符的数量
        dict_t = Counter(t)
        required = len(dict_t)  # 有多少种字符

        # 滑动窗口左右指针
        left, right = 0, 0
        formed = 0  # 当前窗口满足t中字符种类的情况下的长度

        window_counts = {}  # 这个字典记录当前窗口字符种类和数量

        # 结果: 窗口长度, left, right
        result = float("inf"), None, None

        while right < len(s):
            character = s[right]
            window_counts[character] = window_counts.get(character, 0) + 1

            # 当某个字符数量满足要求的时候 formed + 1
            if character in dict_t and window_counts[character] == dict_t[character]:
                formed += 1

            # 当前窗口满足要求时，尝试收缩窗口
            while left <= right and formed == required:
                character = s[left]
                # 更新最小窗口
                if right - left + 1 < result[0]:
                    result = (right - left + 1, left, right)
                window_counts[character] -= 1

                # 如果某个字符的数量变少了，不符合t的要求了，formed - 1
                if character in dict_t and window_counts[character] < dict_t[character]:
                    formed -= 1

                # 左指针右移
                left += 1

            # 继续扩大窗口
            right += 1

        # 如果没有找到满足条件的窗口，返回空
        if result[0] == float("inf"):
            return ""
        else:
            return s[result[1]:result[2] + 1]


if __name__ == "__main__":
    solution = Solution()
    s, t = "ADOBECODEBANC", "ABC"
    print(solution.minWindow(s, t))  # 应该输出"BANC"

    s1, t1 = "a", "a"
    print(solution.minWindow(s1, t1))
