import asyncio
from array import array
import sounddevice as sd
from scipy.io.wavfile import write
import pyaudio
import io
import os

CHUNK_SIZE = 1024
MIN_VOLUME = 2600
BUF_MAX_SIZE = CHUNK_SIZE * 10
q = asyncio.Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))
stop_event = asyncio.Event()

async def main():
    listener_task = asyncio.create_task(listen(q))
    recorder_task = asyncio.create_task(record(q))
    await asyncio.gather(listener_task, recorder_task)

async def record(q):
    pause_timer = 1
    while not stop_event.is_set():
        chunk = await q.get()
        vol = max(chunk)
        if vol >= MIN_VOLUME:
            pause_timer = 1
        else:
            pause_timer = pause_timer + 1
            if pause_timer == 50:
                print("break now")
                #os.system('python runner.py')
                stop_event.set()

async def listen(q):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )

    while not stop_event.is_set():
        try:
            await q.put(array('h', stream.read(CHUNK_SIZE)))
        except asyncio.queues.QueueFull:
            return  # discard

if __name__ == '__main__':
    asyncio.run(main())