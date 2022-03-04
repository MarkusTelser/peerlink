from dataclasses import dataclass
from math import ceil
from struct import pack
from src.backend.metadata.Bencoder import bdecode, bencode


class MetadataIDs:
    REQUEST = 0
    DATA = 1
    REJECT = 2


@dataclass
class MetadataRequest:
    piece: int = -1


@dataclass
class MetadataData:
    piece: int = -1
    total_size: int = -1
    data: bytes = b''


@dataclass
class MetadataReject:
    piece: int = -1


def val_metadata_msg(bdata: bytes):
    data, r = bdecode(bdata[6:], spare_bytes=True)

    if "msg_type" not in data:
        raise Exception('Message type field not in metadata msg')
    if "piece" not in data:
        raise Exception('Piece field not in metadata message')

    if data['msg_type'] == MetadataIDs.REQUEST:
        return val_metadata_request(data)
    elif data['msg_type'] == MetadataIDs.DATA:
        return val_metadata_data(data, r)
    elif data['msg_type'] == MetadataIDs.REJECT:
        return val_metadata_reject(data)
    else:
        # TODO logger.log('unknown message type in metadata msg')
        pass


def val_metadata_request(data: dict):
    piece = data['piece']
    return MetadataRequest(piece)


def val_metadata_data(data: dict, metadata: bytes):
    if "total_size" not in data:
        raise Exception('Total size field not in data message')
    if ceil(data['total_size'] / 16384) - 1 != data['piece'] and len(metadata) != 16384:
        raise Exception('Metadata piece doesnt have fixed size of 16384 bytes')
    if ceil(data['total_size'] / 16384) - 1 == data['piece']:
        if len(metadata) != data['total_size'] - 16384 * (ceil(data['total_size'] / 16384) - 1):
            raise Exception('Last metadata piece has wrong size')
    
    piece = data['piece']
    total_size = data['total_size']
    return MetadataData(piece, total_size, metadata)


def bld_extension_msg(ext_id: int, payload: bytes):
    length = 2 + len(payload)

    msg = pack("!IB", length, 20)
    msg += pack("!B", ext_id)
    msg += pack(f"!{len(payload)}s", payload)
    
    return  msg


def val_metadata_reject(data: dict):
    piece = data['piece']
    return MetadataReject(piece)

def bld_metadata_request(mid: int, piece: int):
    data = {
        'msg_type': MetadataIDs.REQUEST,
        'piece': piece
    }

    payload = bencode(data)
    return bld_extension_msg(mid, payload)

def bld_metadata_data(mid: int, piece: int, bdata: bytes):
    data = {
        'msg_type': MetadataIDs.DATA,
        'piece': piece,
        'total_size': len(bdata)
    }

    payload = bencode(data)
    payload += bdata
    return bld_extension_msg(mid, payload)

def bld_metadata_reject(mid: int, piece: int):
    data = {
        'msg_type': MetadataIDs.REJECT,
        'piece': piece
    }

    payload = bencode(data)
    return bld_extension_msg(mid, payload)
