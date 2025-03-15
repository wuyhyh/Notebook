from typing import List
import random


class Solution:
    def quick_sort(self, nums: List[int], left: int, right: int) -> List[int]:
        if left >= right:
            return

        # 选取基准元素进行分区
        pivot_index = self.partition(nums, left, right)
        self.quick_sort(nums, left, pivot_index - 1)
        self.quick_sort(nums, pivot_index + 1, right)

    def partition(self, nums: List[int], left: int, right: int) -> int:
        # 随机选择基准，然后交换到最后
        pivot_index = random.randint(left, right)
        nums[right], nums[pivot_index] = nums[pivot_index], nums[right]

        pivot = nums[right]  # 选取最右边元素作为基准
        i = left  # i指向比pivot小的元素的下一个位置

        for j in range(left, right):
            if nums[j] < pivot:
                nums[i], nums[j] = nums[j], nums[i]  # 交换元素
                i += 1

        # 将基准元素放在正确的位置
        nums[i], nums[right] = nums[right], nums[i]
        return i

    def sort_array(self, nums: List[int]) -> List[int]:
        self.quick_sort(nums, 0, len(nums) - 1)
        return nums


if __name__ == '__main__':
    solution = Solution()
    list_case = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    res = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    if solution.sort_array(list_case) == res:
        print(list_case)
