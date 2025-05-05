#1次元reduceの定義

def reduce(op,List):

    
    if op == 'add' :
        return reduce_1d_add(List)
    elif op == 'mul':
        return reduce_1d_mul(List)
    else :
        print("error")

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

