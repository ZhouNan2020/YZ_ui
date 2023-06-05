def tes():
    print("hello")
    return "hello"

# 增加一个复杂的函数，示范Cpython的执行过程
def add(a, b):
    c = a + b
    return c
# 继续
def add2(a, b):
    c = a + b
    return c
# 怎么使用cdef
cdef int a = 1
cdef int b = 2
cdef int c = a + b
return c
