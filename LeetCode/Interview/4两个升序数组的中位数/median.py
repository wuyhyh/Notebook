from typing import List


class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # 让nums1始终是较短的数组
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        # 对nums1进行二分查找，寻找合适的切分位置 cut_pos_1
        len_1, len_2 = len(nums1), len(nums2)
        total_len = len_1 + len_2
        left, right = 0, len_1

        while left <= right:
            cut_pos_1 = (left + right) // 2
            cut_pos_2 = (total_len + 1) // 2 - cut_pos_1

            # 根据切分位置计算边界的值
            max_left_2 = float("-inf") if cut_pos_2 == 0 else nums2[cut_pos_2 - 1]
            min_right_2 = float("inf") if cut_pos_2 == len_2 else nums2[cut_pos_2]
            max_left_1 = float("-inf") if cut_pos_1 == 0 else nums1[cut_pos_1 - 1]
            min_right_1 = float("inf") if cut_pos_1 == len_1 else nums1[cut_pos_1]

            # 检查是否满足切分条件
            if max_left_1 <= min_right_2 and max_left_2 <= min_right_1:
                if total_len % 2 == 1:  # 总数为奇数
                    return max(max_left_1, max_left_2)
                return (max(max_left_1, max_left_2) + min(min_right_1, min_right_2)) / 2
            # 调整二分查找的范围
            elif max_left_1 > min_right_2:  # nums1的切分位置导致左边的数的最大值太大了
                right = cut_pos_1 - 1
            else:
                left = cut_pos_1 + 1


if __name__ == '__main__':
    sol = Solution()
    nums1 = [1, 3]
    nums2 = [2]
    print(sol.findMedianSortedArrays(nums1, nums2))
