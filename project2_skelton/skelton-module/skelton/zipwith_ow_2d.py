import numpy as np


def zipwith_ow_2d(Func, List1, List2) :

    l1 = len(List1)
    l2 = len(List2)

    if l1 != l2 :
        print("error\n")

    for i in range(l1):
        l3 = len(List1[i])
        l4 = len(List2[i])

        if l3 != l4 :
            print("error\n")
        for j in range(l3):
            List1[i][j] = Func(List1[i][j].item() if isinstance(List1[i][j], np.generic) else List1[i][j],List2[i][j].item() if isinstance(List2[i][j], np.generic) else List2[i][j])
