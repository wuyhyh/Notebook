def solveNQueens(n):
    def backtrack(row, cols, diag1, diag2, board):
        # 如果已经放置完所有的皇后
        if row == n:
            result.append(["".join(row) for row in board])
            return

        for col in range(n):
            # 检查列、主对角线、副对角线是否有冲突
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue

            # 做选择：将当前列、主对角线、副对角线标记为已占用
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)

            # 放置皇后并继续处理下一行
            board[row][col] = 'Q'
            backtrack(row + 1, cols, diag1, diag2, board)

            # 撤销选择
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    result = []
    board = [['.' for _ in range(n)] for _ in range(n)]  # 初始化棋盘
    cols = set()  # 记录已占用的列
    diag1 = set()  # 记录已占用的主对角线
    diag2 = set()  # 记录已占用的副对角线
    backtrack(0, cols, diag1, diag2, board)
    return result
