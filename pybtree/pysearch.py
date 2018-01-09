"""Search algorithms adapted from https://github.com/btrevizan/ordernsearch.git."""


def def_key(x):
    """Return the element to compare with.

    Keyword arguments:
        x -- object of any kind
    """
    return x


def search(sequence, n, key=def_key, how='binary'):
    """Search an element n in a sequence.

    Keyword arguments:
        sequence -- a 1darray to order
        n -- element to be searched
        key -- function that retrive a singular element
        (default is the element itself)
        how -- {'linear', (default 'binary')}
    """
    return eval('{}(sequence, n, key)'.format(how))


def linear(sequence, n, key=def_key):
    """Search an element linearly and return its first index.

    Return None, if element does not exists.

    Keyword arguments:
        sequence -- a 1darray to order
        n -- element to be searched
        key -- function that retrive a singular element
        (default is the element itself)

    Note: the element is already a singular element
    """
    length = len(sequence)

    if length == 0:
        return None

    # For each element...
    for i in range(length):

        # If sequence[i] is the element, return its index
        if n == key(sequence[i]):
            return i

    # Did not find the element
    return None


def binary(sequence, n, key=def_key):
    """Search an element by binary means and return its first index.

    Return None, if element does not exists.

    Keyword arguments:
        sequence -- a 1darray to order
        n -- element to be searched
        key -- function that retrive a singular element
        (default is the element itself)

    Note: the element is already a singular element.
    The sequence should be order in a ascending order.
    """
    length = len(sequence)

    if length == 0:
        return None

    j = 0               # start
    k = length          # stop
    i = (j + k) // 2    # middle

    while j <= i:
        # If sequence[i] is the element, return its index
        if n == key(sequence[i]):
            return i
        elif j == i:
            return None
        elif n < key(sequence[i]):
            k = i  # update stop
        else:
            j = i  # update start

        i = (j + k) // 2

    # Did not find the element
    return None
