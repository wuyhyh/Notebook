def spiralOrder(matrix):
    # 如果矩阵为空，直接返回空列表
    if not matrix:
        return []

    result = []

    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # 遍历上边界
        for i in range(left, right + 1):
            result.append(matrix[top][i])
        top += 1

        # 遍历右边界
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1

        # 遍历下边界，必须判断 top <= bottom，避免重复遍历已遍历的行
        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(matrix[bottom][i])
            bottom -= 1

        # 遍历左边界，必须判断 left <= right，避免重复遍历已遍历的列
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1

    return result
