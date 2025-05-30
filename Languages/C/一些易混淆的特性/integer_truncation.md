整数截断（Integer Truncation）是指在将一个较大的整数类型转换为较小的整数类型时，超过目标类型能容纳的位数部分被截断，从而可能导致数据丢失或数值变化的现象。截断的主要原因是目标类型的位宽不足以存储源类型的所有位。

截断的工作原理

假设我们有一个32位的int变量，尝试将它转换成8位的signed char类型。int类型可以表示较大的范围，而signed char类型仅能表示从-128到127的范围。因此，当超过8位的数据转换为8位时，只保留低8位，较高的位会被截断。

截断的例子

举例来说，假设我们有一个int变量，其值为300：

300 的二进制（32位表示）：00000000 00000000 00000001 00101100

当我们将其转换为8位的signed char时，只会保留低8位：

截断后的 8 位：00101100（即十进制的 44）

因此，300在截断后变成了44，发生了数据丢失。

实际应用

整数截断在数据类型转换、函数参数传递（尤其是不同位宽的参数）和数组索引等操作中很常见。为了避免截断引起的错误，通常要确保转换后的类型能够容纳原类型的数据范围。

示例代码
```c
#include <stdio.h>

int main()
{
	int a = 300;
	signed char b = (signed char)a; // 截断操作

	printf("a = %d\n", a);		// 输出 300
	printf("b = %d\n", b); // 输出 44（因为300截断成8位后变为44）

	return 0;
}
```
在这个例子中，a的值300在转换为signed char类型后被截断，结果变成了44，而不是原始值300。

总结

整数截断是将较大位宽的整数转换为较小位宽的整数时导致的数据丢失现象。截断会导致数值的变化，可能引发逻辑错误或意料之外的结果。因此，进行类型转换时应特别注意目标类型的范围是否足够容纳原始数据。