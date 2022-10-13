from dataclasses import dataclass
import smokesignal

@dataclass
class TT:
    RESUME = 0
    PAUSED = 1

class MMM():
    def __init__(self):
        self.t = TT.RESUME

@smokesignal.on('foo')
def called(txt: str):
    print('recv signal')
    print('args: '+ txt)