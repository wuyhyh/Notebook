def searchMatrix(matrix, target):
    if not matrix:
        return False

    m, n = len(matrix), len(matrix[0])
    row, col = 0, n - 1  # 从右上角开始

    while row < m and col >= 0:
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            col -= 1  # 向左移动
        else:
            row += 1  # 向下移动

    return False
