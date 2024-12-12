class Solution:
    def majorityElement(self, nums):
        candidate = None
        count = 0

        # 第一遍遍历，选举出候选元素
        for num in nums:
            if count == 0:
                candidate = num
                count = 1
            elif num == candidate:
                count += 1
            else:
                count -= 1

        return candidate
