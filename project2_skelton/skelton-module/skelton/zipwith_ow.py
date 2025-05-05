import numpy as np


def zipwith_ow(Func, List1, List2) :

    l1 = len(List1)
    l2 = len(List2)

    if l1 != l2 :
        print("error\n")

    for i in range(l1):
        List1[i] = Func(List1[i].item() if isinstance(List1[i], np.generic) else List1[i],List2[i].item() if isinstance(List2[i], np.generic) else List2[i])

