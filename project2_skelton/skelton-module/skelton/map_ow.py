#上書きmapの定義
import numpy as np


def map_ow(Func,List) :
   
   length = len(List)

   for i in range(length) :
        List[i] = Func(List[i].item() if isinstance(List[i], np.generic) else List[i])


