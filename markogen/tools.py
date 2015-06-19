
from random import uniform
from collections import deque
from itertools import islice

def weighted_choice(choices, return_weight=False):
    total = sum(weight for _, weight in choices)
    random_val = uniform(0, total)
    upto = 0
    for choice, weight in choices:
        if upto + weight > random_val:
            return choice, weight if return_weight else choice
        upto += weight
    assert False, "Shouldn't get here"


def sliding_window(seq, size=2):
    seq_it = iter(seq)
    result = deque(islice(seq_it, size), maxlen=size)
    while True:
        yield result
        result.append(next(seq_it))
