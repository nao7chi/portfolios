#上書きしないmapの定義
import numpy as np

def map(Func, List) :
    result = []

    for data in List:
        result.append(Func(data.item() if isinstance(data, np.generic) else data))
    return result
