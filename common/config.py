import os

import toml

if not os.path.exists("config.toml"):
    raise FileNotFoundError("config.toml not found")

config = toml.load("config.toml")
general_config = config["general"]
monitor_config = config["monitor"]
parser_config = config["parser"]
order_config = config["order"]
tgbot_config = config["tgbot"]
