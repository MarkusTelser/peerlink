"""
this file contains all custom exceptions for this application.
this way we can differentiate between exceptions that are 
expected to happen and others that happened out of nowhere

current exception hierachy:
-->TorrentExceptions
   -->NetworkExceptions
   -->MessageExceptions
"""

class TorrentExceptions(Exception):
    pass

""" --Torrent Sub-Exceptions-- """
class NetworkExceptions(TorrentExceptions):
    pass

class MessageExceptions(TorrentExceptions):
    pass

""" --Network Sub-Exceptions-- """

class ConnectTimeout(NetworkExceptions):
    pass

class SendTimeout(NetworkExceptions):
    pass

class ReceiveTimeout(NetworkExceptions):
    pass

class ConnectionRefused(NetworkExceptions):
    pass

class ConnectionClosed(NetworkExceptions):
    pass

class UnknownHost(NetworkExceptions):
    pass

""" --Message Sub-Exceptions-- """


""" --General Sub-Exceptions-- """
class UnknownTrackerType(TorrentExceptions):
    pass

class NotSupportedOperation(TorrentExceptions):
    pass