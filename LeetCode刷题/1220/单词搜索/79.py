def exist(board, word):
    # 定义四个方向：上、下、左、右
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(i, j, word_index):
        # 如果当前索引等于单词长度，表示已经找到完整的单词
        if word_index == len(word):
            return True

        # 边界检查
        if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]):
            return False

        # 如果当前字符不匹配，返回 False
        if board[i][j] != word[word_index]:
            return False

        # 记录当前字符，并将其标记为已访问
        temp = board[i][j]
        board[i][j] = '#'

        # 递归搜索四个方向
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if dfs(ni, nj, word_index + 1):
                return True

        # 恢复当前字符，回溯
        board[i][j] = temp
        return False

    # 遍历每个字符作为起始点
    for i in range(len(board)):
        for j in range(len(board[0])):
            if dfs(i, j, 0):  # 从当前位置开始搜索
                return True

    return False
