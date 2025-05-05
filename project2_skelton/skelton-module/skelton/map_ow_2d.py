#上書きする2次元mapの定義
import numpy as np

def map_ow_2d(Func, List) :
    l1 = len(List)

    for i in range(l1):
        l2 = len(List[i])
        for j in range(l2): 
            List[i][j] = Func(List[i][j].item() if isinstance(List[i][j], np.generic) else List[i][j])
