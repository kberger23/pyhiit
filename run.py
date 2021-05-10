import time
from playsound import playsound


def sound_begin():
    playsound('sound/bell_short_1.mp3')


def sound_end():
    playsound('sound/bell_long_1.mp3')


interval = [30]*6
pause = 2

for i, _int in enumerate(interval):
    time.sleep(pause)
    interval_counter = i + 1
    print(f"Starting interval {interval_counter}")
    sound_begin()
    time.sleep(_int)
    sound_end()
    print(f"Finished interval {interval_counter}")

print("Finished session")
sound_end()
