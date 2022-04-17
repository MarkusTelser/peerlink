from src.frontend.utils.utils import to_seconds
import asyncio
import random

class DownloadChart():
    STEPS = 30
    _PERIODS = ['1 min', '10 min', '30 min', '1 h', '6 h', '12 h', '24 h']
    PERIODS = [to_seconds(x) for x in _PERIODS]

    def __init__(self, value_cb):
        super(DownloadChart, self).__init__()
        self.outstanding = [2 for x in self.PERIODS]
        self.data = [[] for _ in range(len(self.PERIODS))]
        self.value_cb = value_cb

    async def execute(self):
        while True:
            print('#' * 100)
            #print(self.outstanding)
            min_interval = int(self.PERIODS[0] / self.STEPS)
            await asyncio.sleep(min_interval)
            expired_items = [i for i, x in enumerate(self.outstanding) if x - min_interval <= 0]

            for item in expired_items:
                self.set_value(item)
            print(expired_items, self.data)
            
            self.outstanding = [(x - min_interval) or (self.PERIODS[i] / self.STEPS) for i, x in enumerate(self.outstanding)]
        
    def set_value(self, pos):
        if pos == 0:
            value = self.value_cb()
            self.append_value(pos, value)
        else:
            prev_interval = self.PERIODS[pos - 1] / self.STEPS
            interval = self.PERIODS[pos] / self.STEPS
            count_steps = int(interval / prev_interval)

            prev_data = self.data[pos - 1][-count_steps:]
            average = sum(prev_data) / len(prev_data)

            self.append_value(pos, average)
            
    def append_value(self, index, value):
        if len(self.data[index]) >= self.STEPS:
            self.data[index].pop(0)
        self.data[index].append(value)
        
        

        
            

async def run():
    d = DownloadChart()
    print(d.PERIODS)
    await d.execute()
    print('RUNN')


if __name__ == '__main__':
    asyncio.run(run())
    print('here')
    