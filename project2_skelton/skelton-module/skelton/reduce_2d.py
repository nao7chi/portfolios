#2次元reduceの定義

def reduce_2d(op1,op2,List):

    reduce_x = []

    if op1 == 'add' :
        for x in List :
            reduce_x.append(reduce_1d_add(x))
    elif op1 == 'mul':
        for x in List :
            reduce_x.append(reduce_1d_mul(x))
    else :
        print("error")

    result = 0.0

    if op2 == 'add' :
        result = reduce_1d_add(reduce_x)
    elif op2 == 'mul':
        result = reduce_1d_mul(reduce_x)
    else :
        print("error")

    return result



def reduce_1d_add(List) :
    result = 0.0

    for data in List:
        result += data
    
    return result

def reduce_1d_mul(List) :
    result = 1.0

    for data in List :
        result *= data

    return result
