from impossible import *

def true_pred(cantor):
    return True

def false_pred(cantor):
    return False

def specific_pred(cantor):
    return cantor[3] and not cantor[4] and cantor[9]

def simple_pred(cantor):
    return cantor[0]

def medium_pred(cantor):
    return cantor[1 - cantor[2]] if cantor[3] else cantor[5 + cantor[4]]

def complex_pred(cantor):
    import math
    pi_str = str(math.pi)
    for i in range(10):
        if cantor[i] != bool(int(pi_str[i+2]) % 2):
            return False
    return True

def test_impossible():
    preds = [true_pred, false_pred, specific_pred, simple_pred, medium_pred, complex_pred]
    for pred in preds:
        # check that pred equals itself, even when referentially distinct
        assert equal(pred, lambda x: pred(x))

        # if pred is not the false pred
        if not equal(pred, lambda _: False):
            # find a cantor that fulfils it
            assert pred(find(pred))
        else:
            assert not for_some(pred)

        # show that all the preds are different unless they're literally the same object
        for pred2 in preds:
            assert pred == pred2 or not equal(pred, pred2)
