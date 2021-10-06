def append_yield(list_, generator):
    for g in generator:
        list_.append(g)
        yield g