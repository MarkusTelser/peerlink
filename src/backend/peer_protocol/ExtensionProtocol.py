import socket
from struct import unpack, pack
from dataclasses import dataclass
from ipaddress import IPv6Address, ip_address
from src.backend.metadata.Bencoder import bdecode, bencode

@dataclass
class HandshakeMessage:
    listen_port: int = -1
    client: str = ""
    yourip: str = ""
    ipv4: str = ""
    ipv6: str = ""
    max_requests: str = -1

class ExtensionProtocol:
    MESSAGE_ID = 20
    HANDSHAKE_ID = 0
    
    def __init__(self):
        self.extensions = dict()
    
    def val_handshake(self, bdata: bytes):
        # check which extended message id
        extended_id = unpack("!B", bdata[5:6])[0]
        if extended_id < 0:
            raise Exception('Extended message id smaller than zero')
        elif extended_id == self.HANDSHAKE_ID:
            print("handshake")
        else:
            print("no handhsake")
        
        msg = HandshakeMessage()
        payload = unpack(f"!{len(bdata) - 6}s", bdata[6:])[0]
        data = bdecode(payload)
        
        # check if no one/two char names in top-level dict
        """
        exceptions = ['m', 'p', 'v']
        for key in data.keys():
            if len(key) < 3 and key not in exceptions:
                raise Exception('Top-level keys have to be longer than 2 characters')
        """
        
        if "m" in data:
            # check that there are no duplicate ids (except 0)
            values = list(data['m'].values())
            for value in values:
                if value != 0 and values.count(value) != 1:
                    raise Exception('Duplicate ids for different message extensions')
                
            # check if there are no one/two character extension names
            keys = list(data['m'].keys())
            for key in keys:
                if len(key) < 3:
                    raise Exception('Extension names have to be longer than 2 characters')
            
            # first received extension handshake
            if len(self.extensions) == 0:
                self.extensions = dict(data['m'])
            # subsequent handshake to enable/disable extensions
            else:
                for ext in dict(data['m']):
                    self.extensions[ext] = dict(data['m'])[ext]
        if "p" in data:
            msg.listen_port = data['p']
        if "v" in data:
            msg.client = data['v']
        if "yourip" in data:
            msg.yourip = data['yourip']
        if "ipv4" in data:
            msg.ipv4 = data['ipv4']
        if "ipv6" in data:
            msg.ipv6 = data['ipv6']
        if "reqq" in data:
            msg.max_requests = data['reqq']
        
        # support subsequent handshake messages to enable/disable extensions
        for extension in self.extensions:
            if extension in data:
                self.extensions[extension] = data[extension]
        

    def bld_handshake(self, client=None, yourip=None, listen_port=None, ipv4=None, ipv6=None, max_requests=None):
        payload = {}
        
        # optional keys in dictionary
        if client != None:
            payload['v'] = client
        if yourip != None:
            address_family = socket.AF_INET 
            if type(ip_address(yourip)) == IPv6Address:
                address_family = socket.AF_INET6
            payload['yourip'] = socket.inet_pton(address_family, yourip)
        if listen_port != None:
            payload['p'] = listen_port
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
        extended_id = self.HANDSHAKE_ID
        payload = bencode(payload)
        length = 2 + len(payload)
        msg = pack("!IB", length, index)
        msg += pack("!B", extended_id)
        msg += pack(f"!{len(payload)}s", payload)
        
        return msg