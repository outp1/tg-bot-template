import random


def safe_list_get(i, idx, default):
    """Returns index of list or default value

    Dict.get method for lists

    """
    try:
        return i[idx]
    except IndexError:
        return default


def generate_id_sync(len_: int = 6, conn_func=None, char_set: str = "1234567890"):
    """Returns a random number of the specified length

    Accepts a function to check if the id in the table matches and iterates until
    it creates a unique id

    """
    while True:
        number = "".join(random.choice(list(char_set)) for i in range(len_))
        if conn_func is None:
            return number
        check = conn_func(number)
        if not check:
            break
    return number


async def generate_id_async(
    len_: int = 6, conn_func=None, char_set: str = "1234567890"
):
    """Returns asynchronously a random number of the specified length

    Accepts a asynchronous function to check if the id in the table matches and iterates until
    it creates a unique id

    """
    while True:
        number = "".join(random.choice(list(char_set)) for i in range(len_))
        if conn_func is None:
            return number
        check = await conn_func(number)
        if not check:
            break
    return number
