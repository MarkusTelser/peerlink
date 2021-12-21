from enum import Enum

class ReservedExtensions(Enum):
    AzureusMessagingProtocol = 0x0
    BitcometExtensionProtocol = 0x1
    BitTorrentLocationAwareProtocol = 0x2
    LibtorrentExtensionProtocol = 0x3
    ExtensionNegotiationProtocol = 0x4
    HybridTorrentLegacyV2Upgrade = 0x5
    NATTraversal = 0x6
    FastExtension = 0x7
    XBTPeerExchange = 0x8
    BitTorrentDHT = 0x9
    XBTMetadataExchange = 0x10


extension_table = [
    (0, 0x80, ReservedExtensions.AzureusMessagingProtocol),
    (0, 0xFF, ReservedExtensions.BitcometExtensionProtocol),
    (1, 0xFF, ReservedExtensions.BitcometExtensionProtocol),
    (2, 0x08, ReservedExtensions.BitTorrentLocationAwareProtocol),
    (5, 0x10, ReservedExtensions.LibtorrentExtensionProtocol),
    (5, 0x01, ReservedExtensions.ExtensionNegotiationProtocol),
    (5, 0x02, ReservedExtensions.ExtensionNegotiationProtocol),
    (7, 0x10, ReservedExtensions.HybridTorrentLegacyV2Upgrade),
    (7, 0x08, ReservedExtensions.NATTraversal),
    (7, 0x04, ReservedExtensions.FastExtension),
    (7, 0x02, ReservedExtensions.XBTPeerExchange),
    (7, 0x01, ReservedExtensions.BitTorrentDHT),
    (7, 0x01, ReservedExtensions.XBTMetadataExchange)
]


def comp_bytes(byte_string, value):
    bits_string = "{0:b}".format(byte_string)
    bits_value = "{0:b}".format(value)
    if int(bits_string) & int(bits_value) == int(bits_value):
        return True
    return False


def get_extensions(reserved_bytes: bytes):
    extensions = list()
    for ext in extension_table:
        byte, value, extension = ext
        if comp_bytes(reserved_bytes[byte], value):
            if extension not in extensions: 
                extensions.append(extension)
    return extensions

if __name__ == "__main__":
    b = b'\x00\x00\x00\x00\x00\x10\x00\x05'
    e = get_extensions(b)
    print(b, e)