def rotate(nums, k):
    # 处理 k 超过数组长度的情况
    n = len(nums)
    k = k % n  # k 可能会大于 n，因此取 k % n

    # 1. 反转整个数组
    nums.reverse()

    # 2. 反转前 k 个元素
    nums[:k] = reversed(nums[:k])

    # 3. 反转后 n-k 个元素
    nums[k:] = reversed(nums[k:])
