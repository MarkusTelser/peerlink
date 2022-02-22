from random import choice, random, randint
from string import ascii_letters
from ..exceptions import *

def az_three_digits(ver: bytes):
    return f'{int(chr(ver[0]), 36)}.{int(chr(ver[1]), 36)}.{int(chr(ver[2]), 36)}'

def az_four_digits(ver: bytes):
    return f'{int(chr(ver[0]), 36)}.{int(chr(ver[1]), 36)}.{int(chr(ver[2]), 36)}.{int(chr(ver[3]), 36)}'

def az_two_maj_two_min(ver: bytes):
    return f'{ver[0:2].decode("utf-8")}.{ver[2:4].decode("utf-8")}'

def az_skip_first_two_maj_two_min(ver: bytes):
    return f'{chr(ver[1])}.{ver[2:4].decode("utf-8")}'

def az_three_digits_mnemonic(ver: bytes):
    mnemonic = ''
    if chr(ver[3]) == 'A':
        mnemonic = "Alpha"
    elif chr(ver[3]) == 'B':
        mnemonic = "Beta"
    return f'{az_three_digits(ver)} {mnemonic}'.strip()

def az_no_version(ver: bytes):
    return 'no version'

# specific client peer id decodings
def az_deluge(ver: bytes):
    letters = 'ABCDE'
    if chr(ver[2]).isdigit():
        return f'{chr(ver[0])}.{chr(ver[1])}.{letters.index(chr(ver[2]))}'
    return f'{chr(ver[0])}.{chr(ver[1])}.{chr(ver[2])}'

def az_transmission(ver: bytes):
    if chr(ver[0]) == '0' and chr(ver[1]) == '0' and chr(ver[2]) == '0':
        return f'0.{chr(ver[3])}'
    elif chr(ver[0]) == '0' and chr(ver[1]) == '0':
        return f'0.{ver[2:4].decode("utf-8")}'
    elif chr(ver[3]) == 'Z' or chr(ver[3]) == 'X':
        return f'{chr(ver[0])}.{ver[1:3].decode("utf-8")}+' # adds plus
    return f'{chr(ver[0])}.{ver[1:3].decode("utf-8")}'

def az_webtorrent(ver: bytes):
    v1 = ver[0:2].decode('utf-8')
    if chr(ver[0]) == '0':
        v1 = chr(ver[1])
    
    v2 = ver[2:4].decode('utf-8')
    if chr(ver[2] == '0'):
        v2 = chr(ver[3])

    return f'{v1}.{v2}'

azureus_style = {
    'AG' : ('Ares', az_three_digits),
    'AN' : ('Ares', az_three_digits),
    'A~' : ('Ares', az_four_digits),
    'AR' : ('Arctic'),
    'AV' : ('Avicora'),
    'AX' : ('BitPump', az_two_maj_two_min),
    'AT' : ('Artemis'),
    'AZ' : ('Azureus', az_four_digits),
    'BB' : ('BitBuddy'),
    'BC' : ('BitComet', az_skip_first_two_maj_two_min), # after version 0.59
    'BE' : ('BitTorrent SDK'),
    'BF' : ('Bitflu', az_no_version),
    'BG' : ('BTG (uses Rasterbar libtorrent)', az_four_digits),
    'bk' : ('BitKitten (libtorrent)'),
    'BR' : ('BitRocket'),
    'BS' : ('BTSlave'),
    'BT' : ('BitTorrent', az_three_digits_mnemonic),
    'BW' : ('BitWombat'),
    'BX' : ('Bittorrent X'),
    'CB' : ('Shareaza Plus'),
    'CD' : ('Enhanced CTorrent', az_two_maj_two_min),
    'CT' : ('CTorrent'),
    'DE' : ('DelugeTorrent', az_deluge),
    'DP' : ('Propagate Data Client'),
    'EB' : ('EBit'),
    'ES' : ('electric sheep', az_three_digits),
    'FC' : ('FileCroc'),
    'FG' : ('FlashGet', az_skip_first_two_maj_two_min),
    'FT' : ('FoxTorrent/RedSwoosh'),
    'FW' : ('FrostWire'),
    'FX' : ('Freebox BitTorrent'),
    'GR' : ('GetRight'),
    'GS' : ('GSTorrent'),
    'HL' : ('Halite', az_three_digits),
    'HN' : ('Hydranode'),
    'KG' : ('KGet'),
    'KT' : ('KTorrent'),
    'LC' : ('LeechCraft'),
    'LH' : ('LH:ABC'),
    'LK' : ('linkage', az_three_digits),
    'LP' : ('Lphant', az_two_maj_two_min),
    'LT' : ('libtorrent (Rasterbar)'),
    'lt' : ('libTorrent (Rakshasa)'),
    'LW' : ('LimeWire', az_no_version),
    'MO' : ('MonoTorrent'),
    'MP' : ('MooPolice', az_three_digits),
    'MR' : ('Miro'),
    'MT' : ('MoonlightTorrent'),
    'NE' : ('BT Next Evolution', az_three_digits),
    'NX' : ('Net Transport'),
    'OS' : ('OneSwarm', az_four_digits),
    'OT' : ('OmegaTorrent'),
    'PC' : ('CacheLogic'),
    'PD' : ('Pando'),
    'PE' : ('PeerProject'),
    'PT' : ('Popcorn Time'),
    'pX' : ('pHoeniX'),
    'qB' : ('qBittorrent', az_deluge),
    'QD' : ('QQDownload'),
    'QT' : ('Qt 4 Torrent example'),
    'RT' : ('Retriever'),
    'RZ' : ('RezTorrent'),
    'S~' : ('Shareaza alpha/beta'),
    'SB' : ('~Swiftbit'),
    'SD' : ('Xunlei (Thunderbolt)'),
    'SG' : ('GS Torrent', az_four_digits),
    'SN' : ('ShareNET'),
    'SP' : ('BitSpirit', az_three_digits),
    'SS' : ('SwarmScope'),
    'ST' : ('SymTorrent'),
    'st' : ('sharktorrent'),
    'SZ' : ('Shareaza'),
    'TG' : ('Torrent GO'),
    'TN' : ('TorrentDotNET'),
    'TR' : ('Transmission', az_transmission),
    'TS' : ('Torrentstorm'),
    'TT' : ('TuoTu', az_three_digits),
    'UE' : ('µTorrent Embedded NAS', az_three_digits_mnemonic),
    'UL' : ('uLeecher!'),
    'UM' : ('µTorrent Mac', az_three_digits_mnemonic),
    'UT' : ('µTorrent', az_three_digits_mnemonic),
    'UW' : ('µTorrent Web', az_three_digits_mnemonic),
    'VG' : ('Vagaa', az_four_digits),
    'WD' : ('WebTorrent Desktop'),
    'WT' : ('BitLet'),
    'WW' : ('WebTorrent', az_webtorrent),
    'WY' : ('FireTorrent (Wyzo)'),
    'XC' : ('XTorrent'),
    'XF' : ('Xfplay', az_transmission),
    'XL' : ('Xunlei (Thunderbolt)'),
    'XT' : ('XanTorrent'),
    'XX' : ('Xtorrent'),
    'ZT' : ('ZipTorrent'),
    '7T' : ('aTorrent'),
    'ZO' : ('Zona', az_four_digits),
    '#@' : ('Invalid PeerID')
}

shadow_style = {
    'A' : 'ABC',
    'O' : 'Osprey Permaseed',
    'Q' : 'BTQueue',
    'R' : 'Tribler',
    'S' : 'Shad0ws Client',
    'T' : 'BitTornado',
    'U' : 'UPnP NAT Bit Torrent'
}

mainline_style = {
    'M' : 'Mainline',
    'Q' : 'Queen Bee',
    'S3-' : 'Amazon AWS S3'
}

fixed_style = {
    '346------' : 'TorrenTopia 1.90',
    'AZ2500BT' : 'BitTyrant (Azureus fork) 1.1',
    '-UT170-' : 'uTorrent 1.7.0 RC',
    'Azureus' : 'Azureus 1',
    '-aria2-' : 'Aria 2',
    'PRC.P---' : 'BitTorrent Plus! II',
    'P87.P---' : 'BitTorrent Plus!',
    'S587Plus' : 'BitTorrent Plus!',
    'BLZ' : 'Blizzard Downloader',
    'btuga' : 'BTugaXP',
    'oernu' : 'BTugaXP',
    'BTDWV-' : 'Deadman Walking',
    'Deadman Walking-' : 'Deadman',
    'Ext' : 'External Webseed',
    '271-' : 'GreedBT 2.7.1',
    'arclight' : 'Hurricane Electric',
    '-WS' : 'HTTP Seed',
    '10-------' : 'JVtorrent',
    'LIME' : 'Limewire',
    'martini' : 'Martini Man',
    'Pando' : 'Pando',
    'PEERAPP' : 'PeerApp',
    'a00---0' : 'Swarmy',
    'a02---0' : 'Swarmy',
    'T00---0' : 'Tweeweety',
    'DansClient' : 'XanTorrent',
    '-MG1' : 'MediaGet',
    '-MG21' : 'MediaGet 2.1',
    '-G3' : 'G3 Torrent'
}
"""
missing peer ids, because they have weird formats and are probably quite rare
so in case I will ever have too much time on my hand, I implement these weird formats
but they will probably stay unimplemented forever:
(just in case they are listed here)

starts with Azureus | pos 5 | = Azureus 2.0.3.2
starts with BG | pos 5 | = BTGetit
starts with BTuga | pos 5 | = BTugaXP  
starts with btfans | pos 4 | = SimpleBT

support custom version format:
starts with DNA | = BitTorrent DNA
starts with OP | = Opera  # Pre build 10000 versions
starts with O | = Opera # Post build 10000 versions
starts with Mbrst | = Burst!
starts with turbobt | = TurboBT
starts with btpd | BT Protocol Daemon
starts with Plus | = Plus!
starts with XBT | = XBT
starts with -BOW | = BitsOnWheels
starts with eX | = eXeem
starts with -ML | = MLdonkey
starts with BitLet | = Bitlet
starts with AP | = AllPeers
starts with BTM | BTuga Revolution
starts with RS | pos 2 | = Rufus
starts with BM | pos 2 | = BitMagnet # BitMagnet - predecessor to Rufus
starts with QVOD | = QVOD
starts with TB | = Top-BT # Top-BT is based on BitTornado, but doesn't quite stick to Shadow's naming conventions
starts with TIX | = Tixati
starts with -FL | = folx # seems to have a sub-version encoded in following 3 bytes, not worked out how: "folx/1.0.456.591" : 2D 464C 3130 FF862D 486263574A43585F66314D5A
starts with -UM | = µTorrent Mac
starts with -UT | = µTorrent # UT 3.4+

XBT Client: XBT + xxx + (d(=Debug client) or -(standard client)) + - + random # xxx = ASCii digits 5.4.3
Opera 8 preview + Opera 9.x: OP + xxxx + random # xxx = four digits that equal build number
ML donkey: -ML + dotted version + - + random # e.g. -ML2.7.2-kgjjfkd
Bits on Wheels: -BOW + xxx + - + random # x = three digit version  Version 1.0.6 has xxx = A0C
BitSpirit: ends in UDP0, rest unclear
Rufus: first two decimal ascii values version + (RS or BM) + random
AllPeers: AP + version string + -
"""


class PeerIDs:
    @staticmethod
    def generate():
        # pretend to be a qbittorrent for the moment (changed afterwards)
        return "-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12))
    
    @staticmethod
    def generate_key():
        # key with atleast 32 bit entrophy for identification with peer id
        return ''.join(choice(ascii_letters) for _ in range(4))
    
    @staticmethod
    def generate_ikey():
        # equivalten to generate_key but for UDP Tracker
        return randint(0, 9999)
    
    @staticmethod
    def get_client(pid: bytes):
        client = "unknown"
        version = -1
        
        if len(pid) != 20:
            raise WrongFormat("Peer id isnt't 20 bytes long")
        
        # identify spoof clients
        if pid.endswith(b'UDP0') or pid.endswith(b'HTTPBT'):
            # bit spirit client
            if pid[2:4] == b'BS':
                client = 'BitSpirit'
                version = chr(pid[1])
                if version == '0':
                    version = '1'
                return client, version
            # bit comet client
            else:
                mod_ver = None
                if pid.startswith(b'exbc'):
                    mod_ver = '(Standard)'
                elif pid.startswith(b'FUTB'):
                    mod_ver = '(Solidox Mod)'
                elif pid.startswith(b'xUTB'):
                    mod_ver = '(Mod 2)'
                    
                if mod_ver != None:
                    max_ver = chr(pid[4])
                    try:
                        version = f'{max_ver}.{pid[5:7].decode("utf-8")}'
                    except UnicodeDecodeError:
                        raise WrongType('min version is not decoded in utf-8')
                    if pid[6:10] == b'LORD':
                        client = 'BitLord'
                        if max_ver != '0':
                            version = f'{max_ver}{"0" + chr(pid[5])}'
                    else:
                        client = 'BitComet'
                    return client, version
                        
        # identify azeurus style
        if chr(pid[0]) == '-' and chr(pid[7]) == '-':
            id_bytes = pid[1:3]
            try:
                cid = id_bytes.decode('utf-8')
            except UnicodeDecodeError:
                raise WrongType('azeurus id bytes are not decoded in utf-8')
            if cid in azureus_style:
                # use default encoding 
                if type(azureus_style[cid]) == str:
                    client = azureus_style[cid]
                    version = az_four_digits(pid[3:7])
                # use custom defined encoding func
                elif type(azureus_style[cid]) == tuple:
                    client, func = azureus_style[cid]
                    version = func(pid[3:7])
                return client, version
        
        # identify mainline style
        for key in mainline_style:
            try:
                if key == str(pid[0:len(key)].decode('utf-8')):
                    client = mainline_style[key]
                    temp = pid[len(key):]
                    v1 = temp[0:temp.find(b'-')].decode('utf-8')
                    temp = temp[temp.find(b'-')+1:]
                    v2 = temp[0:temp.find(b'-')].decode('utf-8')
                    temp = temp[temp.find(b'-')+1:]
                    v3 = temp[0:temp.find(b'-')].decode('utf-8')
                    if temp.find(b'-') != -1:
                        version = f"{v1}.{v2}.{v3}"
                        return client, version
            except UnicodeDecodeError:
                raise WrongType('mainline key or version not decoded in utf-8')
            
        # identify shadow style
        if chr(pid[0]) in shadow_style:
            v_numbers = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            client = shadow_style[chr(pid[0])]
            versions = list()
            for i in range(5):
                if chr(pid[1+i]) == '-':
                    break
                if v_numbers.find(chr(pid[i+1])) == -1:
                    raise WrongType('shadow version number is not in valid version dataset')
                versions.append(str(v_numbers.find(chr(pid[i+1]))))
            if pid[6:9] == b'---':
                version = '.'.join(versions)
                return client, version
        
        return client, version