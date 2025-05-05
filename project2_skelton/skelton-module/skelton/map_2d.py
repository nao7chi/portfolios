#上書きしない2次元mapの定義
import numpy as np

def map_2d(Func, List) :
    result = []

    for l1 in List:
        for i in l1: 
            result.append(Func(i.item() if isinstance(i, np.generic) else i))
    return result
