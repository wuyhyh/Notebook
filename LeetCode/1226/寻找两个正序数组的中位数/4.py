def findMedianSortedArrays(nums1, nums2):
    # 确保 nums1 是较小的数组，这样我们在 nums1 上做二分查找
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    left, right = 0, m
    median = 0.0

    while left <= right:
        # 在 nums1 上进行二分查找
        partition1 = (left + right) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # 获取 nums1 和 nums2 的左右部分的最大最小值
        maxLeft1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        minRight1 = float('inf') if partition1 == m else nums1[partition1]

        maxLeft2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        minRight2 = float('inf') if partition2 == n else nums2[partition2]

        # 检查是否满足条件
        if maxLeft1 <= minRight2 and maxLeft2 <= minRight1:
            # 如果总长度是偶数
            if (m + n) % 2 == 0:
                median = (max(maxLeft1, maxLeft2) + min(minRight1, minRight2)) / 2
            else:
                median = max(maxLeft1, maxLeft2)
            return median
        elif maxLeft1 > minRight2:
            right = partition1 - 1
        else:
            left = partition1 + 1

    raise ValueError("Input arrays are not sorted.")
