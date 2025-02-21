def trap(height):
    # 如果高度数组为空，则无法接住任何雨水
    if not height:
        return 0

    n = len(height)
    left, right = 0, n - 1  # 左右指针，分别指向数组的开头和末尾
    left_max, right_max = 0, 0  # 左右两侧的最大高度初始化为 0
    water = 0  # 用于存储最终计算出的雨水总量

    # 双指针向中间收缩，计算每个位置可以存储的雨水量
    while left < right:
        # 如果左侧的高度小于右侧的高度
        if height[left] < height[right]:
            # 如果当前左侧的高度大于或等于左侧的最大高度，更新左侧最大高度
            if height[left] >= left_max:
                left_max = height[left]
            else:
                # 否则，计算当前柱子上可以接住的雨水量，并累加到总水量中
                water += left_max - height[left]
            # 左指针右移，继续计算下一个位置
            left += 1
        else:
            # 如果右侧的高度小于或等于左侧高度
            # 如果当前右侧的高度大于或等于右侧的最大高度，更新右侧最大高度
            if height[right] >= right_max:
                right_max = height[right]
            else:
                # 否则，计算当前柱子上可以接住的雨水量，并累加到总水量中
                water += right_max - height[right]
            # 右指针左移，继续计算下一个位置
            right -= 1

    return water  # 返回总的雨水量

# 示例用法
height = [0,1,0,2,1,0,1,3,2,1,2,1]
print(trap(height))  # 输出: 6
