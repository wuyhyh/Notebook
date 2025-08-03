# C 语言实现快速排序 - 视频讲解文稿

---

## 🎬 开场介绍（10 秒）

大家好，我是宇航，这里是我的技术分享频道。本期视频我们来实现一个经典算法 —— 快速排序。快速排序是一种高效的排序算法，广泛应用于实际工程中。今天我们将用
C 语言完整实现它，并一步步讲清原理。

---

## 🧠 快速排序原理讲解（1 分钟）

快速排序（Quick Sort）使用的是分治（Divide and Conquer）策略，核心思想如下：

1. **选择一个基准值（pivot）**：一般选择最后一个元素或者中间元素。
2. **划分数组（Partition）**：把数组划分成两部分，左边的元素都小于基准值，右边的元素都大于基准值。
3. **递归排序左右两部分**：对左右两部分分别继续进行快速排序，直到子数组长度为 1。

快速排序的平均时间复杂度是 O(n log n)，在数据随机分布的情况下性能非常好。

---

## 🧑‍💻 快速排序代码讲解（主内容）

### 1. 交换函数 swap

```c++
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
```

* 这是一个经典的交换两个变量值的函数。
* 使用指针传参，使得可以交换数组中的两个元素。

### 2. 分区函数 partition

```c++
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}
```

* `pivot` 是基准值，这里选的是最后一个元素。
* `i` 指向小于区间的尾部。
* 遍历数组，小于 pivot 的元素前移。
* 最后把 pivot 放到正确的位置。

### 3. 快速排序函数 quicksort

```c++
void quicksort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}
```

* 核心递归过程。
* 先对当前区间进行划分，再分别递归左子区间和右子区间。

### 4. 辅助函数：打印数组

```c++
void print_array(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}
```

* 简单的输出数组函数，帮助我们验证排序结果。

### 5. 主函数 main

```c++
int main() {
    int arr[] = {7, 2, 1, 6, 8, 5, 3, 4};
    int size = sizeof(arr) / sizeof(arr[0]);

    printf("原始数组: ");
    print_array(arr, size);

    quicksort(arr, 0, size - 1);

    printf("排序后数组: ");
    print_array(arr, size);

    return 0;
}
```

* 初始化一个无序数组。
* 打印原始数组。
* 调用 quicksort 排序。
* 打印排序后数组。

---

## 🔁 演示排序过程（可视化建议）

你可以选择用注释或手动追踪方式展示每一步 partition 的过程，尤其是第一次划分时数组如何被分为两边。

例如：

```
初始数组: [7, 2, 1, 6, 8, 5, 3, 4]
选择 pivot = 4
第一轮划分结果: [2, 1, 3] [4] [7, 6, 8, 5]
```

---

## 📌 总结（10 秒）

快速排序是一种高效的排序算法，在面试中也非常常见。今天我们用 C 语言从头实现了它，并讲清了原理和流程。欢迎点赞关注，我们下期见。

---

## 📎 附：本次讲解代码打包下载（可在视频下方附 GitHub 链接）

