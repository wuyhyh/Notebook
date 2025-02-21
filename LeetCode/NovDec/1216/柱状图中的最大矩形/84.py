def largestRectangleArea(heights):
    # 添加一个高度为0的柱子，以确保栈中所有元素都能被处理
    heights.append(0)
    stack = []
    max_area = 0

    for i in range(len(heights)):
        # 如果栈为空或当前柱子的高度大于栈顶柱子的高度，将当前柱子的索引压入栈
        while stack and heights[i] < heights[stack[-1]]:
            h = heights[stack.pop()]  # 弹出栈顶柱子，计算它的矩形面积
            w = i if not stack else i - stack[-1] - 1  # 如果栈为空，宽度为i，否则为当前索引和栈顶索引的差
            max_area = max(max_area, h * w)  # 更新最大面积
        stack.append(i)  # 将当前柱子的索引压入栈

    return max_area
