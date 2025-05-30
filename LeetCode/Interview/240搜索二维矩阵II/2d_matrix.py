from typing import List


class Solution:
    def search_matrix(self, matrix: List[List[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False

        m, n = len(matrix), len(matrix[0])
        row, col = 0, n - 1

        # 从右上角开始搜索
        while row < m and col >= 0:
            current = matrix[row][col]
            if current == target:
                return True
            elif current > target:
                col -= 1  # 值太大了，向左搜索
            else:
                row += 1  # 值太小了，向下搜索

        return False


if __name__ == '__main__':
    sol = Solution()
    matrix = [
        [1, 4, 7, 11, 15],
        [2, 5, 8, 12, 19],
        [3, 6, 9, 16, 22],
        [10, 13, 14, 17, 24],
        [18, 21, 23, 26, 30]
    ]

    print(sol.search_matrix(matrix, 11))
    print(sol.search_matrix(matrix, 110))
