import asyncio
from collections import deque
import time
from src.backend.peer_protocol.PieceManager import PieceManager

class SpeedMeasurer:
    MEASURE_PERIOD = 30
    MEASURE_INTERVAL = 2
    MAX_ITEMS = MEASURE_PERIOD // MEASURE_INTERVAL
    
    def __init__(self, piece_manager: PieceManager):
        self.piece_manager = piece_manager
        self.down_measurements = deque() 
    
    
    async def execute(self):
        while True:
            t = time.time()
            
            self.down_measurements.append(int(self.piece_manager.downloaded_bytes))
            
            # pop oldest measurement if queue is too big
            if len(self.down_measurements) > SpeedMeasurer.MAX_ITEMS:
                self.down_measurements.popleft()
            
            delta_time = SpeedMeasurer.MEASURE_INTERVAL - (time.time() - t)
            print("\\" * 100, delta_time, self.down_measurements)
            await asyncio.sleep(delta_time)
    
    
    @property
    def avg_down_speed(self):
        return self._convert_mibps(self.raw_down_speed)
    
    @property
    def raw_down_speed(self):
        if len(self.down_measurements) > 1:
            diff_time = (len(self.down_measurements) - 1) * SpeedMeasurer.MEASURE_INTERVAL
            diff_bytes = self.down_measurements[-1] - self.down_measurements[0]
            avg_down_speed = diff_bytes / diff_time
            return avg_down_speed
        return 0

    @property
    def eta(self):
        pass
    
    def _convert_mibps(self, bits: int):
        if bits < 1000:
            return f"{bits} B/s"
        if bits / 1024 < 1000:
            return f"{int(round(bits / 1024, 0))} KiB/s"
        elif bits / (1024 ** 2) < 1000:
            return f"{round(bits / (1024 ** 2), 1)} MiB/s"
        elif bits  / (1024 ** 3) < 1000:
            return f"{round(bits / (1024 ** 3), 2)} GiB/s"
        elif bits / (1024 ** 4) < 1000: 
            return f"{round(bits / (1024 ** 4), 2)} TiB/s"
        elif bits / (1024 ** 5) < 1000:
            return f"{round(bits / (1024 ** 5), 3)} PiB/s"