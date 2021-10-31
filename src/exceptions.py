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

class NetworkExceptions(Exception):
    pass

class MessageExceptions(Exception):
    pass

""" --Network Sub-Exceptions-- """

class SendTimeoutException(NetworkExceptions):
    pass

class ReceiveTimeoutException(NetworkExceptions):
    pass

""" --Message Sub-Exceptions-- """

class InvalidResponseException(MessageExceptions):
    pass