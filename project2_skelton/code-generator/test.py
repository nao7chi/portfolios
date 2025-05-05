#埋め込みDSLを用いた記述例

import skelton 

from dataclass import Data

WIDTH = 2
HEIGHT = 2
def f (x):
    return x - ave
def g (x):
    return x * x

data1 = Data(1)
data1.data = [1,2,3,4,5,6,7,8]
ave = skelton.reduce("add",data1,8)
ave = ave / 8
a = skelton.map(f,data1,8)
skelton.map_ow(g,a,8)
re = skelton.reduce("add",a,8)
print(re)