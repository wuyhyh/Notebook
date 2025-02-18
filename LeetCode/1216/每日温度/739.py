def dailyTemperatures(temperatures):
    n = len(temperatures)
    answer = [0] * n  # 初始化答案数组
    stack = []  # 用栈来存储索引

    for i in range(n):
        # 当栈不为空且当前温度大于栈顶所表示的温度
        while stack and temperatures[i] > temperatures[stack[-1]]:
            index = stack.pop()  # 弹出栈顶元素，得到前面那个温度较低的天数索引
            answer[index] = i - index  # 计算从那个天数到当前天数的天数差
        stack.append(i)  # 将当前天数索引压入栈中

    return answer
