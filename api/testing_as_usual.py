
import requests

jsons = {
    "get_hash": True,
    "app": "telegram",
    "number": "87789197489"
}

json2 = {
    "get_hash": False,
    "app": "telegram",
    "bot_name": "purple_guy",
    "secret_key": "nHneySnM6QDGuHs8",
    "code": 72913,
    "accept_code": True,
}

json3 = {
    "app": "whatsapp"
}
resp = requests.post("http://127.0.0.1:2731/settgtoken", headers={}, json=jsons)

