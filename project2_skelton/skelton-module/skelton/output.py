#skelton用のprint

def output(x,l) :

    if l == list :
        x = [i for i in x if i != 0.0]

        if not(x) : 
            x.append(0.0)
    
    print(x)
