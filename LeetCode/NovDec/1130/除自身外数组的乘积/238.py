def productExceptSelf(nums):
    n = len(nums)

    # 初始化输出数组
    output = [1] * n

    # 计算前缀积并存储到 output 数组中
    prefix_product = 1
    for i in range(n):
        output[i] = prefix_product
        prefix_product *= nums[i]

    # 计算后缀积并与前缀积结合
    suffix_product = 1
    for i in range(n-1, -1, -1):
        output[i] *= suffix_product
        suffix_product *= nums[i]

    return output
