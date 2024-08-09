import random

from common.config import general_config


def choice_rpc_node() -> str:
    rpc_nodes = general_config["rpc_nodes"]
    if not rpc_nodes:
        raise ValueError("No RPC nodes found")
    return random.choice(rpc_nodes)
