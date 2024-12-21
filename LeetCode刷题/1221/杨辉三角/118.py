def generate(numRows):
    result = []

    # 遍历生成每一行
    for i in range(numRows):
        # 每行的第一个元素和最后一个元素都是 1
        row = [1] * (i + 1)

        # 中间的元素是上一行对应元素之和
        for j in range(1, i):
            row[j] = result[i - 1][j - 1] + result[i - 1][j]

        result.append(row)

    return result
