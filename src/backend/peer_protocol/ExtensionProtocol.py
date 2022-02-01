import socket
from struct import unpack, pack
from dataclasses import dataclass
from ipaddress import IPv6Address, ip_address
from src.backend.metadata.Bencoder import bdecode, bencode

@dataclass
class HandshakeMessage:
    pass

class ExtensionProtocol:
    MESSAGE_ID = 20
    
    def __init__(self):
        pass
    
    def val_handshake(self, bdata: bytes):
        extended_id = unpack("!B", bdata[5:6])[0]
        print(extended_id)
        if extended_id == 0:
            print("handshake")
        else:
            print("no handhsake")
        
        payload = unpack(f"!{len(bdata) - 6}s", bdata[6:])[0]
        data = bdecode(payload)

        print(data)
        if "m" in data:
            pass
        elif "p" in data:
            pass
        elif "v" in data:
            pass
        elif "yourip" in data:
            pass
        elif "ipv6" in data:
            pass
        elif "ipv4" in data:
            pass
        elif "reqq" in data:
            pass
        
        # support deactivating extension support
        
    # libtorrent extended protocol 
    def bld_handshake(self, client_version=None, yourip=None, tcp_port=None, ipv4=None, ipv6=None, max_requests=None):
        payload = {}
        
        # optional keys in dictionary
        if client_version != None:
            payload['v'] = client_version
        if yourip != None:
            address_family = socket.AF_INET 
            if type(ip_address(yourip)) == IPv6Address:
                address_family = socket.AF_INET6
            payload['yourip'] = socket.inet_pton(address_family, yourip)
        if tcp_port != None:
            payload['p'] = tcp_port
        if ipv4 != None:
            compact = socket.inet_pton(socket.AF_INET, ipv4)
            payload['ipv4'] = compact
        if ipv6 != None:
            compact = socket.inet_pton(socket.AF_INET6, ipv6)
            payload['ipv6'] = compact
        if max_requests != None:
            payload['reqq'] = max_requests
        
        # supported extension based on this
        payload['m'] = {
            'LT_metadata': 1,
            'ut_pex':	2
        }
        
        # data to binary
        index = self.MESSAGE_ID
        extended_id = 0
        payload = bencode(payload)
        length = 2 + len(payload)
        msg = pack("!IB", length, index)
        msg += pack("!B", extended_id)
        msg += pack(f"!{len(payload)}s", payload)
        
        return msg