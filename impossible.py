class Cantor(object):
    """A representation of a function from the natural
    numbers into bools. Alternatively, a representation
    of an infinite-length list of bools"""
    def __init__(self, func):
        self.func = func
        
    def __getitem__(self, index):
        return self.func(index)

    def __radd__(self, bools):
        def new_func(index):
            if index < len(bools):
                return bools[index]
            return self[index - len(bools)]
        return Cantor(new_func)

    def __str__(self):
        return "[{self[0]}, {self[1]}, {self[2]}, ...]".format(self=self)

    def to_string(self, precision):
        return "[{}...]".format("".join("X" if self[x] else "_" for x in range(precision)))

def for_some(pred):
    cantor = Cantor(lambda i: find(pred)[i])
    return pred(cantor)

def for_every(pred):
    not_pred = lambda cantor: not pred(cantor)
    return not(for_some(not_pred))

def find(pred):
    if for_some(lambda cantor: pred([False] + cantor)):
        return [False] + Cantor(lambda i: find(lambda cantor: pred([False] + cantor))[i])
    else:
        return [True] + Cantor(lambda i: find(lambda cantor: pred([True] + cantor))[i])

def search(pred):
    if for_some(pred):
        return find(pred)
    return None

def pred(cantor):
    import math
    pi_str = str(math.pi)
    for i in range(10):
        if cantor[i] != bool(int(pi_str[i+2]) % 2):
            return False
    return True

def equal(pred1, pred2):
    def pred3(cantor):
        return pred1(cantor) == pred2(cantor)
    return for_every(pred3)
