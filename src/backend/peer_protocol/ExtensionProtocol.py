import socket
from struct import unpack, pack
from dataclasses import dataclass
from ipaddress import IPv6Address, ip_address
from src.backend.metadata.Bencoder import bdecode, bencode
from src.backend.peer_protocol.Metadata import val_metadata_msg

@dataclass
class ExtensionHandshakeMessage:
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
        self.supported_ext = {
            'ut_metadata': 1
        }
        
    def val_extension_msg(self, bdata: bytes):
        # check which extended message id
        extended_id = unpack("!B", bdata[5:6])[0]
        print('/'*50, extended_id, self.supported_ext)
        if extended_id < 0:
            raise Exception('Extended message id smaller than zero')
        elif extended_id == self.HANDSHAKE_ID:
            return self.val_handshake(bdata)
        elif extended_id in self.supported_ext.values():
            ext_name = [k for k, v in self.supported_ext.items() if v == extended_id][0]
            
            # parse different messages implemented through extension protocol
            if ext_name == 'ut_metadata':
                return val_metadata_msg(bdata)
            
        else:
            raise Exception('Invalid extended id, not matching any registered names', extended_id, self.extensions, self.supported_ext)
    
    def val_handshake(self, bdata: bytes):
        msg = ExtensionHandshakeMessage()
        data = bdecode(bdata[6:])
        
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
            if type(data['yourip']) == str:
                data['yourip'] = bytes(data['yourip'], 'utf-8')
            if len(data['yourip']) == 4:
                msg.yourip = socket.inet_ntop(socket.AF_INET, data['yourip'])
            elif len(data['yourip']) == 16:
                msg.yourip = socket.inet_ntop(socket.AF_INET6, data['yourip'])
            else:
                pass# TODO console.log(yourip field invalid size)
        if "ipv4" in data:
            if type(data['ipv4']) == str:
                data['ipv4'] = bytes(data['ipv4'], 'utf-8')
            msg.ipv4 = socket.inet_ntop(socket.AF_INET, data['ipv4'])
        if "ipv6" in data:
            if type(data['ipv6']) == str:
                data['ipv6'] = bytes(data['ipv6'], 'utf-8')
            msg.ipv6 = socket.inet_ntop(socket.AF_INET6, data['ipv6'])
        if "reqq" in data:
            msg.max_requests = data['reqq']
        
        # support subsequent handshake messages to enable/disable extensions
        for extension in self.extensions:
            if extension in data:
                self.extensions[extension] = data[extension]
                
        return msg
    
    @staticmethod
    def bld_extension_msg(ext_id: int, payload: bytes):
        length = 2 + len(payload)

        msg = pack("!IB", length, ExtensionProtocol.MESSAGE_ID)
        msg += pack("!B", ext_id)
        msg += pack(f"!{len(payload)}s", payload)
        
        return  msg

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
            payload['ipv4'] = socket.inet_pton(socket.AF_INET, ipv4)
        if ipv6 != None:
            payload['ipv6'] = socket.inet_pton(socket.AF_INET6, ipv6)
        if max_requests != None:
            payload['reqq'] = max_requests
        
        # supported extension based on this
        payload['m'] = self.supported_ext
        
        # data to binary
        id = ExtensionProtocol.HANDSHAKE_ID
        payload = bencode(payload)
        return ExtensionProtocol.bld_extension_msg(id, payload)