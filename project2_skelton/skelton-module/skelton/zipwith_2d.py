import numpy as np


def zipwith_2d(Func, List1, List2) :

    l1 = len(List1)
    l2 = len(List2)

    result = []

    if l1 != l2 :
        print("error\n")

    for i in range(l1):
        l3 = len(List1[i])
        l4 = len(List2[i])

        if l3 != l4 :
            print("error\n")
        for j in range(l3):
            result.append(Func(List1[i][j].item() if isinstance(List1[i][j], np.generic) else List1[i][j],List2[i][j].item() if isinstance(List2[i][j], np.generic) else List2[i][j]))
    
    return result

"""
テスト用
"""
def add(x,y) :
    return x+y

d1 = [[1,2,3],[7,8,9]]
d2 = [[4,5,6],[10,11,12]]

print(zipwith_2d(add,d1,d2))

