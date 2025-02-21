def setZeroes(matrix):
    # 记录第一行和第一列是否需要置零
    first_row_zero = any(matrix[0][j] == 0 for j in range(len(matrix[0])))
    first_col_zero = any(matrix[i][0] == 0 for i in range(len(matrix)))

    # 使用第一行和第一列作为标记
    for i in range(1, len(matrix)):  # 从第二行开始
        for j in range(1, len(matrix[0])):  # 从第二列开始
            if matrix[i][j] == 0:
                matrix[i][0] = 0  # 标记第i行
                matrix[0][j] = 0  # 标记第j列

    # 根据标记将相应的元素置为零
    for i in range(1, len(matrix)):
        for j in range(1, len(matrix[0])):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0

    # 处理第一行
    if first_row_zero:
        for j in range(len(matrix[0])):
            matrix[0][j] = 0

    # 处理第一列
    if first_col_zero:
        for i in range(len(matrix)):
            matrix[i][0] = 0
