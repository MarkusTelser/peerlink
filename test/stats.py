from src.frontend.utils.utils import to_seconds

def len(intervals, steps):
    per = list()
    i = 0
    previous = 0
    for interval in intervals:
        time_step = interval / steps
        steps_in_previous = previous / time_step
        print(time_step, steps_in_previous)

        previous = interval 
        i += steps - steps_in_previous
        per.append(steps - steps_in_previous)
    return i, per

i = ['1 min', '10 min', '30 min', '1 h', '6 h', '12 h', '24 h']
i = [to_seconds(x) for x in i]

print(i)
print(len(i, 30))