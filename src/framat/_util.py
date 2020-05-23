import itertools


def enumerate_with_step(iterable, start=0, step=1):
    """
    TODO
    https://stackoverflow.com/questions/24290025/python-enumerate-downwards-or-with-a-custom-step
    """

    for x in iterable:
        yield (start, x)
        start += step


def pairwise(iterable):
    """
    Return a new iterator which yields pairwise items

    s --> (s0,s1), (s1,s2), (s2, s3), ...

    See: https://docs.python.org/3/library/itertools.html#itertools-recipes
    """

    a, b = itertools.tee(iterable)
    next(b, None)

    return zip(a, b)


