from collections import namedtuple
from src.backend.metadata.Bencoder import bencode,bdecode

PingMessage = namedtuple("PingMessage", "tid id") 
FindNodeMessage = namedtuple("FindNodeMessage", "tid id") 
GetPeersMessage = namedtuple("GetPeersMessage", "tid id") 
AnnouncePeerMessage = namedtuple("AnnouncePeerMessage", "tid id",) 

ErrorMessage = namedtuple("ErrorMessage", "tid id code msg") 

def bld_query(tid, method, params={}):
    msg = {
        "y": "q",
        "q": method,
        "t": tid,
        "a": params
    }
    return bencode(msg)

def bld_ping(tid, my_id):
    params = { "id" : my_id }
    return bld_query(tid, "ping", params)

def bld_find_node(tid, my_id, target):
    params = { "id" : my_id, "target" : target }
    return bld_query(tid, "find_node", params)

def bld_get_peers(tid, my_id, info_hash):
    params = { "id": my_id, "info_hash": info_hash }
    return bld_query(tid, "get_peers", params)

def bld_announce_peer(tid, my_id, info_hash, port, token, implied_port=False):
    params = { 
        "id" : my_id,
        "info_hash": info_hash,
        "port": port,
        "token": token,
        "implied_port": implied_port
    }
    return bld_query(tid, "announce_peer", params)

def parse(msg):
    dec = bdecode(msg)

    if "t" not in dec:
        pass
    if "y" not in dec:
        pass

    if dec["y"] == "q":
        pass
    elif dec["y"] == "r":
        pass
    elif dec["y"] == "e":
        pass
    else:   
        pass
    
    if "v" in dec:
        pass 
    
def val_ping():
    pass

def val_find_node():
    pass

def val_get_peers():
    pass

def val_announce_peer():
    pass

print(bld_ping("aa", "abcdefghij0123456789"))