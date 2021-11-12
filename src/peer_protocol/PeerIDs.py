from random import choice
from string import ascii_letters

peer_ids = {
    '' : '',
    '' : ''
}

class PeerIDs:
    @staticmethod
    def generate():
        return "-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12))

    @staticmethod
    def get_client(pid):
        pass