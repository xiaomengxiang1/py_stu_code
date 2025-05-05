# ------------------介绍和安装以及性能对比---------------------

# numpy的底层是c所以效率较高

# 实现两个数组的加法
# 数组 A 是 1~N 数字的平方
# 数组 B 是 1~N 数字的立方
# import numpy as np
# def python_sum(n):
#     """ Python实现数组的加法
#     @param n: 数组的长度
#     """
#     a = [i**2 for i in range(n)]
#     b = [i**3 for i in range(n)]
#     c = []
#     for i in range(n):
#         c.append(a[i] + b[i])
#     return c

# def numpy_num(n):
#     """numpy实现数组的加法
#     @param n:数组的长度
#     """
#     a = np.arange(n) ** 2
#     b = np.arange(n) ** 3
#     return a + b
    

# ------------------数组的创建方法和函数---------------------
# Numpy 的 array 和 Python 的 List 的一个区别，是它元素必须都是同一种数据类型，
# 比如都是数字 int 类型，这也是 Numpy 高性能的一个原因；

# array 本身的属性
    # shape：返回一个元组，表示 array 的维度(行和列)
    # ndim：一个数字，表示 array 的维度的数目
    # size：一个数字，表示 array 中所有数据元素的数目
    # dtype：array 中元素的数据类型

# import numpy as np
# # 创建一个一维数组
# x = np.array([1,2,3,4,5])

# # 二维数组
# y = np.array([
#     [1,2,3,4],
#     [2,3,4,5]
# ])

# 创建只含有1的数组
# import numpy as np
# a = np.ones(4)
# print(a)
# # [1. 1. 1. 1.]

# b = np.ones((2,3))
# print(b)
# # [[1. 1. 1.]
# #  [1. 1. 1.]]

# 同理
# np.zeros创建全为0的数组

# import numpy as np
# print(np.full((2,2), 666))
# [[666 666]
#  [666 666]]