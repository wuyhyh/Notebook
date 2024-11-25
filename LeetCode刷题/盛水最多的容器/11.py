# 问题 11: 盛最多水的容器
# 给定 n 个非负整数 a1, a2, ..., an，其中每个整数代表坐标 (i, ai) 上的一点。
# 画 n 条垂直线，使得每条线的两个端点分别为 (i, ai) 和 (i, 0)。
# 找出两条线，使得它们与 x 轴形成的容器可以容纳最多的水。

from typing import List

def maxArea(height: List[int]) -> int:
    left, right = 0, len(height) - 1
    max_area = 0

    while left < right:
        # 计算当前左右指针形成的面积
        width = right - left
        current_height = min(height[left], height[right])
        current_area = width * current_height
        # 如果当前面积大于最大面积，则更新最大面积
        max_area = max(max_area, current_area)

        # 移动指针
        # 将较短的线向中间移动，以期找到更大的面积
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_area

# 示例用法
height = [1,8,6,2,5,4,8,3,7]
print(maxArea(height))  # 输出: 49
