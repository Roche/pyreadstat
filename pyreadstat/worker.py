
def worker(inpt):
    offset, chunksize, path, read_function, kwargs = inpt
    df, meta = read_function(path, row_offset=offset, row_limit=chunksize, **kwargs)
    return df