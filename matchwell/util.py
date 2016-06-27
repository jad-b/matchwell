def walk(val, level=0, leaves=True):
    """Walk a structure made of a dicts/lists."""
    if isinstance(val, dict):
        for k, v in sorted(val.items()):
            yield k, level
            yield from walk(v, level + 1, leaves=leaves)
    elif isinstance(val, list):
        for item in val:

            yield from walk(item, level + 1, leaves=leaves)
    elif leaves:
        yield val, level


def tree(struct, filtr=''):
    gen = walk(struct)
    for key, lvl in gen:
        if key in filtr:
            yield next(gen)
