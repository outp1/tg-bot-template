from utils.func_tools import generate_id_sync


def generate_base_id(conn_func=None):
    return int(generate_id_sync(conn_func=conn_func))
