class Solution:
    def singleNumber(self, nums):
        result = 0
        for num in nums:
            result ^= num  # 对每个数进行异或
        return result
