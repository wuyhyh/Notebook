v4 实现了一个完整的 ADT，但是使用定长数组的实现方式有缺点。
指定了数组的上限值之后，我们就不能拥有不同容量的栈了。有2种方法可以解决这个问题。
动态数组的实现和链表的实现。

我们先使用动态数组来实现。这个方法的关键是修改`stack_type`使contents成员指向数组的指针，而不是数组本身。
```c
struct stack_type{
    Item *contents;
    int top;
    int size;
};
```
