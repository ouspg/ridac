


def yieldSliceIndexes(n,minsize, maxsize):
    sliceSize = maxsize
    while sliceSize >= minsize:
        #print sliceSize
        for begin, end in yieldSizeWindows(sliceSize, n):
            yield (begin, end)
        sliceSize -= 1


def yieldSizeWindows(sliceSize, n):
    for end in range(sliceSize, n+1):
        begin = end - sliceSize
        yield (begin, end)
