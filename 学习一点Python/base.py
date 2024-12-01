print("print something")
a, b = 0, 1
while a < 10:
    print(a, end='x')
    a, b = b, a + b

squares = list(map(lambda x: x ** 2, range(10)))
print(squares)

import fibo

fibo.fib0(10)
res = fibo.fib1(20)
print(res)

print(fibo.__name__)

fib = fibo.fib1

print(fib(100))

print(dir())
