def rotate(matrix):
    n = len(matrix)

    # 1. 转置矩阵
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    # 2. 水平翻转每一行
    for i in range(n):
        matrix[i].reverse()
