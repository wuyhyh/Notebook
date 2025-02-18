在C语言中，**字符串处理函数**主要定义在`<string.h>`库中，用于处理以空字符 `\0` 结尾的字符串。以下是一些高频的字符串处理函数及其常见用途：

### 1. **字符串长度计算**

- **`strlen`**：计算字符串的长度（不包含终止符 `\0`）。
  ```c
  #include <string.h>
  size_t len = strlen("hello"); // len = 5
  ```

### 2. **字符串拷贝**

- **`strcpy`**：将源字符串复制到目标字符串。
  ```c
  char dest[20];
  strcpy(dest, "hello");
  ```

- **`strncpy`**：拷贝指定长度的字符串，避免超出目标缓冲区的边界。
  ```c
  strncpy(dest, "hello", 3); // 只拷贝前三个字符
  ```

### 3. **字符串拼接**

- **`strcat`**：将源字符串追加到目标字符串的末尾，目标字符串需要有足够空间。
  ```c
  char str[20] = "hello ";
  strcat(str, "world"); // str = "hello world"
  ```

- **`strncat`**：拼接指定长度的字符串，避免超出缓冲区边界。
  ```c
  strncat(str, "world", 3); // 只拼接 "wor"
  ```

### 4. **字符串比较**

- **`strcmp`**：按字典顺序比较两个字符串。
    - 返回`0`表示相等，`<0`表示第一个字符串小于第二个字符串，`>0`表示第一个字符串大于第二个字符串。
  ```c
  int result = strcmp("hello", "world"); // result < 0
  ```

- **`strncmp`**：比较指定长度的字符串。
  ```c
  int result = strncmp("hello", "helium", 3); // 比较前3个字符
  ```

### 5. **字符串查找**

- **`strchr`**：查找字符在字符串中首次出现的位置。
  ```c
  char *pos = strchr("hello", 'e'); // 返回指向 'e' 的指针
  ```

- **`strrchr`**：查找字符在字符串中最后一次出现的位置。
  ```c
  char *pos = strrchr("hello", 'l'); // 返回指向第二个 'l' 的指针
  ```

- **`strstr`**：查找子字符串在字符串中首次出现的位置。
  ```c
  char *pos = strstr("hello world", "world"); // 返回指向 "world" 的指针
  ```

### 6. **字符串分割**

- **`strtok`**：将字符串分割为多个子字符串（以指定的分隔符为界），逐次调用可以遍历所有子字符串。
  ```c
  char str[] = "hello world";
  char *token = strtok(str, " ");
  while (token != NULL) {
      printf("%s\n", token);
      token = strtok(NULL, " ");
  }
  ```

### 7. **字符串转化**

- **`atoi`**：将字符串转换为整数。
  ```c
  int num = atoi("123"); // num = 123
  ```

- **`atof`**：将字符串转换为浮点数。
  ```c
  double num = atof("123.45"); // num = 123.45
  ```

- **`strtol`**、`strtoll`**、`strtod`** 等：可以指定进制、处理更大的数值类型，适用于更复杂的字符串转换。
  ```c
  long int num = strtol("123", NULL, 10); // 十进制转换为长整型
  ```

### 8. **字符串填充和复制**

- **`memset`**：将指定字符填充到内存块中，通常用于初始化字符串或内存。
  ```c
  char str[10];
  memset(str, 'a', 9); // 前9个字符填充为 'a'
  str[9] = '\0';       // 添加结束符
  ```

- **`memcpy`**：复制内存块，适用于任何类型的数据，不限于字符串。
  ```c
  char src[10] = "hello";
  char dest[10];
  memcpy(dest, src, strlen(src) + 1); // 包括结束符一同复制
  ```

### 9. **字符串替换**

标准库中没有直接的字符串替换函数，但可以通过查找与拼接的方式实现，例如替换字符串中的所有某字符或子串。

### 总结

| 函数       | 用途                   |
|------------|------------------------|
| `strlen`   | 获取字符串长度         |
| `strcpy`   | 复制字符串             |
| `strncpy`  | 复制指定长度的字符串   |
| `strcat`   | 拼接字符串             |
| `strncat`  | 拼接指定长度的字符串   |
| `strcmp`   | 比较字符串             |
| `strncmp`  | 比较指定长度的字符串   |
| `strchr`   | 查找字符首次出现位置   |
| `strrchr`  | 查找字符最后出现位置   |
| `strstr`   | 查找子字符串           |
| `strtok`   | 分割字符串             |
| `atoi`     | 转换字符串为整数       |
| `atof`     | 转换字符串为浮点数     |
| `strtol`   | 转换字符串为长整型     |
| `memset`   | 填充内存               |
| `memcpy`   | 复制内存块             |

这些函数是C语言字符串处理的核心函数，对于操作和处理字符串有很大的帮助。使用时要特别注意内存越界等问题，尤其是字符串复制和拼接类函数。
