from struct import pack, unpack
from socket import inet_ntoa, inet_aton
from dataclasses import dataclass
from src.backend.metadata.Bencoder import bencode,bdecode


@dataclass
class DHTMsg:
    tid: str = ""
    type: str = ""
    version: str = ""

@dataclass 
class ErrorMsg(DHTMsg):
    error_code: int = -1
    error_msg: str = ""

@dataclass
class PingQueryMsg(DHTMsg):
    nid: bytes = b''

@dataclass
class BasicRespMsg(DHTMsg):
    nid: bytes = b''

@dataclass
class FindNodeQueryMsg(DHTMsg):
    nid: bytes = b''
    target: str = ""

@dataclass
class FindNodeRespMsg(DHTMsg):
    nid: bytes = b''
    nodes: set = ()

@dataclass
class GetPeersQueryMsg(DHTMsg):
    nid: bytes = b''
    info_hash: str = ""

@dataclass
class GetPeersRespMsg(DHTMsg):
    nid: bytes = b''
    token: str = ""
    nodes: set = ()
    values: str = ""

@dataclass
class AnnouncePeerQueryMsg(DHTMsg):
    nid: bytes = b''
    info_hash: str = ""
    port: int = -1
    token: str = ""
    implied_port: bool = False


def parse(msg):
    dec = bdecode(msg)

    # check if required keys are present
    if "t" not in dec:
        raise Exception("Transaction Id not in msg")
    if "y" not in dec:
        raise Exception("Message Type not in msg")

    # --- PARSE ERRORS
    if dec["y"] == "e":
        ret = ErrorMsg()

        if "e" not in dec:
            raise Exception("Error Field not in msg")
        if len(dec["e"]) != 2:
            raise Exception("Invalid length of Error Field")

        try:
            ret.error_code = int(dec["e"][0])
            ret.error_msg = str(dec["e"][1])
        except:
            raise Exception("Invalid Values for Error Field")
    # --- PARSE QUERIES
    elif dec["y"] == "q":
        if "q" not in dec:
            raise Exception("Method Name not in msg")
        if "a" not in dec:
            raise Exception("Arguments Field not in msg")

        if dec["q"] == "ping":
            ret = PingQueryMsg()
        elif dec["q"] == "find_node":
            ret = FindNodeQueryMsg()

            if "target" not in dec["a"]:
                raise Exception("Target Field not in find_node query")

            try:
                ret.target = str(dec["a"]["target"])
            except: 
                raise Exception("Invalid Value for Target Field")
        elif dec["q"] == "get_peers":
            ret = GetPeersQueryMsg()

            if "info_hash" not in dec["a"]:
                raise Exception("Info_hash Field not in get_peers query")

            try:    
                ret.info_hash = str(dec["a"]["info_hash"])
            except:
                raise Exception("Invalid Value for Info_hash Field")
        elif dec["q"] == "announce_peer":
            ret = AnnouncePeerQueryMsg()

            if "info_hash" not in dec["a"]:
                raise Exception("Info_hash Field not in announce_peer query")
            if "port" not in dec["a"]:
                raise Exception("Port Field not in announce_peer query")
            if "token" not in dec["a"]:
                raise Exception("Token Field not in announce_peer query")
            
            try:
                ret.info_hash = str(dec["a"]["info_hash"])
                ret.port = int(dec["a"]["port"])
                ret.token = str(dec["a"]["token"])

                if "implied_port" in dec["a"]:
                    ret.implied_port = bool(int(dec["a"]["implied_port"]))
            except:
                raise Exception("Invalid Values for announce_peer query")
        else:
            raise Exception("Unknown Method Name in query")

        if "id" not in dec["a"]:
            raise Exception("Node Id not in query")
        try:
            ret.nid = dec["a"]["id"]
        except:
            raise Exception("Invalid Value for Node Id")
    # --- PARSE RESPONSES
    elif dec["y"] == "r":
        if "r" not in dec:
            raise Exception("Response Field not in msg")

        # get_peers response
        if "token" in dec["r"]:
            ret = GetPeersRespMsg()
            if "nodes" in dec["r"]:
                try:
                    ret.nodes = _parse_nodes(dec["r"]["nodes"])
                except:
                    raise Exception("Invalid value for Nodes")
            elif "values" in dec["r"]:
                try:
                    ret.values = _parse_values(dec["r"]["values"])
                except:
                    raise Exception("Invalid value for Values")
            else:
                raise Exception("Neither nodes or values in get_peers response")

            try:
                ret.token = str(dec["r"]["token"])
            except:
                raise Exception("Invalid value for Token")
        # find_node response
        elif "nodes" in dec["r"]:
            ret = FindNodeRespMsg()

            try:
                ret.nodes = _parse_nodes(dec["r"]["nodes"])
            except:
                raise Exception("Invalid value for Nodes")
        # ping+announce_peer response
        else:
            ret = BasicRespMsg()

        if "id" not in dec["r"]:
            raise Exception("Node Id not in response")
        try:
            ret.nid = dec["r"]["id"]
        except:
            raise Exception("Invalid Value for Node Id")
    # --- PARSE UNKNOWN MESSAGE TYPES
    else:   
        raise Exception("Unknown Message Type")
    
    try:
        ret.tid = dec["t"]
        ret.type = {"q": "query", "r": "response", "e": "error"}[dec["y"]]

        if "v" in dec:
            ret.version = dec["v"]
    except:
        raise Exception("Invalid id, type, version in msg")

    return ret

def bld_ping_query(tid, my_id):
    params = { "id" : my_id }
    return _bld_query_msg(tid, "ping", params)

def bld_ping_resp(tid, my_id):
    params = { "id" : my_id }
    return _bld_query_resp(tid, params)

def bld_find_node_query(tid, my_id, target):
    params = { "id" : my_id, "target" : target }
    return _bld_query_msg(tid, "find_node", params)

def bld_find_node_resp(tid, my_id, nodes):
    params = { "id" : my_id, "nodes" : _bld_nodes(nodes) }
    return _bld_query_resp(tid, params)

def bld_get_peers_query(tid, my_id, info_hash):
    params = { "id": my_id, "info_hash": info_hash }
    return _bld_query_msg(tid, "get_peers", params)

def bld_get_peers_resp(tid, my_id, token, values=[], nodes=[]):
    if len(values) == 0 and len(nodes) == 0:
        raise Exception("Neither values or nodes are given")
    elif len(nodes) == 0:
        params = { "id": my_id, "token": token , "values": _bld_values(values)}
    else:
        params = { "id": my_id, "token": token , "nodes": _bld_nodes(nodes)}
    return _bld_query_resp(tid, params)

def bld_announce_peer_query(tid, my_id, info_hash, port, token, implied_port=False):
    params = { 
        "id" : my_id,
        "info_hash": info_hash,
        "port": port,
        "token": token,
        "implied_port": int(implied_port)
    }
    return _bld_query_msg(tid, "announce_peer", params)

def _bld_query_msg(tid, method, params={}):
    msg = {
        "y": "q",
        "q": method,
        "t": tid,
        "a": params
    }
    return bencode(msg)

def _bld_query_resp(tid, answers={}):
    msg = {
        "y": "r",
        "t": tid,
        "r": answers
    }
    return bencode(msg)

def _parse_nodes(nodes):
    if len(nodes) % 26 != 0:
        raise Exception("Invalid length of Nodes(%26)")
    
    l = list()
    for i in range(0, len(nodes), 26):
        ip = inet_ntoa(nodes[i+20:i+24])
        port = unpack("!H", nodes[i+24:i+26])[0]
        l.append([nodes[i:i+20], ip, port])
    return l

# TODO check if values are getting parsed correctly (in reality)
def _parse_values(values):
    l = list()
    for value in values:
        ip = inet_ntoa(value[:4])
        port = unpack("!H", value[4:6])[0]
        l.append([ip, port])
    return l

def _bld_nodes(nodes):
    s = b""
    for node in nodes:
        s += bytes(node[0], "utf-8") if type(node[0]) != bytes else node[0]
        s += inet_aton(node[1])
        s += pack("!H", node[2])
    return s

def _bld_values(values):
    l = list()
    for value in values:
        s = inet_aton(value[0])
        s += pack("!H", value[1])
        l.append(s)
    return l


##
## DEBUG TEST PROGRAM
##
if __name__ == "__main__":
    from collections import OrderedDict
    from src.backend.metadata.Bencoder import bencode
    
    test1 = {"t":"aa", "y":"q", "q":"ping", "a":{"id":"abcdefghij0123456789"}}
    test2 = {"t":"aa", "y":"q", "q":"find_node", "a": {"id":"abcdefghij0123456789", "target":"mnopqrstuvwxyz123456"}}
    test3 = {"t":"aa", "y":"q", "q":"get_peers", "a": {"id":"abcdefghij0123456789", "info_hash":"mnopqrstuvwxyz123456"}}
    test4 = {"t":"aa", "y":"q", "q":"announce_peer", "a": {"id":"abcdefghij0123456789", "implied_port": 1, "info_hash":"mnopqrstuvwxyz123456", "port": 6881, "token": "aoeusnth"}}

    test5 = {"t":"aa", "y":"e", "e":[201, "A Generic Error Ocurred"]}

    print(parse(bencode(test1)))
    print(parse(bencode(test2)))
    print(parse(bencode(test3)))
    print(parse(bencode(test4)))
    print(parse(bencode(test5)))

    test1 = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
    test2 = {"t":"aa", "y":"r", "r": {"id":"0123456789abcdefghij", "nodes": b'G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5\x1bGm3O\xa2'}}
    test3 = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "values": [b'\x1bGm3O\xa2', b'\xbeP\x18\x17oJ']}}
    test4 = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "nodes": b'G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5\x1bGm3O\xa2'}}
    test5 = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
    test6 = OrderedDict([('ip', b'P\xd1\xeeV\x99O'), ('r', OrderedDict([('id', b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'), ('nodes', b"G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5\x1bGm3O\xa2:\xe3\xa6RZ'3) 'G\xf1\xef\xed\x1f;\x8b\x10.\x82\xbeP\x18\x17oJ<\xd6\x04G\x99Z\x0c)\xfc\xe0\xedO[\xden&t\x7ff$ij\xdd\x92\xd6\xf8\x92\xd0y\xc2\xc5\x11^Yy\xd6\xb8\x96\x1b\x1c\x97\x1fOP\xccMn\xaf>\xc2E\xde \xd2,\xcc\x16f\x9a\xe3\xa63\x7f\xe1\xd8 C[cZ(}\xa2\xe7&0\xc4\x91\x8d\xab\x8b\x00z\x1a\xb0\xc4\x98g3e<\xac>\x15\xa8\nZR\xac: \xb7\xd7D\xf9\x13\x81}\x17\x1b\xcc\xf0\x8d\x86Z\x13\xfa\x01\xe7\xb5\x7ft\xc9Hn\x0fDL\x97\x1a\x82\xdd\xa13\xdbV\xc6/\xa0\x89\x11\x1b;\xf3\x1cQ_(cIgZ\xce\xafK\x05\x91\x9b\xde+V\xd6\xc7Z\x98\x99\xe0\\BF\x7f6\xd9\x19?\xa3\x1b?\xa0'0dbPt\x89\xc5L{e\xa5\x85\x0f\x0c\x10\xdd\xcfx\xc9\x1b\r\xbf\x18\xa0S_\xc4\x91\xad?\xbeeN\x15m-\xa4\xb4rE\x05\xael\xb0\x88<}\xa7Ig\xe6EJ\r\xa4\xabO\xefo\xc9\xa1\x18Z\xd3\x8f\xefU\xb6\x1fT\xd4\xdf\xcal\xb3Fq\x0f\xcb\xb4\x89\xe7:\x05\xc6\x80\x12\xa3\xba\x1a\xb2\x04\x80\xbe\xc0N`\x91\\\xed\xd4/\x92:a\xda88888888\x85v0LA\x90R\x03\tm\xce\xb5;Y\xd8\xc8\x9f\x97\xaa,\xfb\x01\xd8\xa6_[\xd4#\xe9\x98ih+\xb1C\x02\xc3\xe7j\xd0>\x04\xe8\xd9\xd2T!c\xb4zJ\xf5=\x14?F\xac{@4z\x99\xad\xd2q\xd3\xd1J\x07\xda")])), ('t', 'aa'), ('y', 'r')])

    print()
    print(parse(bencode(test1)))
    print(parse(bencode(test2)), bencode(test2))
    print(parse(bencode(test3)))
    print(parse(bencode(test4)))
    print(parse(bencode(test5)))
    print(parse(bencode(test6)))

    
    print()
    print(bld_ping_query('aa', "abcdefghij0123456789") == b"d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:t2:aa1:y1:qe")
    print(bld_ping_resp('aa', "mnopqrstuvwxyz123456") == b"d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re")
    print(bld_find_node_query('aa', "abcdefghij0123456789", "mnopqrstuvwxyz123456") == b"d1:ad2:id20:abcdefghij01234567896:target20:mnopqrstuvwxyz123456e1:q9:find_node1:t2:aa1:y1:qe")
    print(bld_find_node_resp('aa', "0123456789abcdefghij", [[b'G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5', '27.71.109.51', 20386]]) == b'd1:rd2:id20:0123456789abcdefghij5:nodes26:G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5\x1bGm3O\xa2e1:t2:aa1:y1:re')
    print(bld_get_peers_query('aa', "abcdefghij0123456789", "mnopqrstuvwxyz123456") == b"d1:ad2:id20:abcdefghij01234567899:info_hash20:mnopqrstuvwxyz123456e1:q9:get_peers1:t2:aa1:y1:qe")
    print(bld_get_peers_resp('aa', "abcdefghij0123456789", "aoeusnth", values=[['27.71.109.51', 20386], ['190.80.24.23', 28490]]) == b'd1:rd2:id20:abcdefghij01234567895:token8:aoeusnth6:valuesl6:\x1bGm3O\xa26:\xbeP\x18\x17oJee1:t2:aa1:y1:re')
    print(bld_get_peers_resp('aa', "abcdefghij0123456789", "aoeusnth", nodes=[[b'G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5', '27.71.109.51', 20386]]) == b'd1:rd2:id20:abcdefghij01234567895:nodes26:G4\x1b\xba\xee4\x82\xd6\xc1p\x11]E\x85M\xef\xb4\xf4\t\xa5\x1bGm3O\xa25:token8:aoeusnthe1:t2:aa1:y1:re')
    print(bld_announce_peer_query('aa', "abcdefghij0123456789", "mnopqrstuvwxyz123456", 6881, "aoeusnth", True) == b"d1:ad2:id20:abcdefghij012345678912:implied_porti1e9:info_hash20:mnopqrstuvwxyz1234564:porti6881e5:token8:aoeusnthe1:q13:announce_peer1:t2:aa1:y1:qe")
    print(bld_ping_resp('aa', "mnopqrstuvwxyz123456") == b"d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re")
    
    print()
    b = b'd1:rd2:id20:2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g5:nodes416:\xd4Kb\xb7\xac\xb4\'V\x84\xc4"\xde\xfe\x8e \x02\x9a\x8f8?\xac\xda\x8e|e\xe5\xe9Z\xb5O\tj\xcf\xab\x12&\x97\x02_\xa3x/\x8eo+\xd7\x9d0\x94\x02\x90\x88|\xe2\xa7\x1af\xe3P*R\x17\xf2}s\xe1s\xa1\xad\xa6\xf0gu\xc2O\xce\xa0\xb9\x0e\xcf\x19\x80%o\x16\x80\x1f\nS=\xa6e\x10d]lv\x19\xbc\xf4\xd4\x98\xc8/?\xa7\x1b\xf1OT\x0f1\xb9c\x05\x90\xd0\xb3\xcc\x8c.\xaeC\xd9\xabL\xbe\xc3\x19\xc4B\xb8\xb4\x99\xf1L\xab\x10\xa7\x901\xf5h\x81\xf9!O\xa9\xb5\x1f\x02>\xe0\x92|\xeb\x85J_v\x8eG\xfa\xd7\xca\xd6\xa7\x06\x06p\xb6t\xdfD\x0c\xc3%p\x10\xb2\xfa#\x90\xa6_\x03\x93\x92\xba\xb0:V\x85\xfa\x9e\xe39\xb5\xdcSbqj\xd3\xfbA" \xcea\x185\tx\xf8k\x14=p\xfb|\xbb\xf8V\x91qx\xbd2/U\x9060\xa2\xcc\xed\xbb\x8b\xa6\x1f\x03Z}\t8%\x1f]\xd4\xcb\xfc\x96\xc8UH\xdb\x0bn8\xcab9\xf0\xad\xc6\xbf\xafH\xfc\x10:\xb3\x19\x86X`\x17\xc9(\xb0\xd6\x98\x12\x95\xe1\xd6\x94"]\xe8\x1e\x01\x96\x08\xef-\xd1Q\xb0\r\xd5\xe2\x82\x04y1"@X\xc5fE8\xb2\xc2DLI\x9atI\x1a\xf6\xf3\x923\xef6\x13\xf2\x941"\xcaV\xc0\xb3\x10g6M5\xce\x10\x7f\nH\x9e\xaa\xffj\x17\x83\xa4\x0c\xaa\xaa\x9d!\xef\x03\xc1p\xfc\xa1\x18\x1d\xc4M\x94\xde\xeax\x96GD\x81\xc7(\xc9\x07\xedBu\xf3\xcb\x930\x11\x90\x87\x90\xcc\xecZ\xbddE\xf7\xf0>\xf0<#\xc4\x9d\x17\x90\xd4\xb2\x82Rs\xf8\x0ee1:t2:aa1:y1:re'
    res = parse(b)
    print(res)
    print(bld_find_node_resp(res.tid, res.nid, res.nodes) == b)