

def safe_list_get (l, idx, default):
    """Returns index of list or default value

Dict.get method for lists 

    """
    try:
        return l[idx]
    except IndexError:
        return default
