import threading
from array import array
from queue import Queue, Full
import sounddevice as sd
from scipy.io.wavfile import write
import pyaudio
import io
import os

CHUNK_SIZE = 1024
MIN_VOLUME = 2600
# if the recording thread can't consume fast enough, the listener will start discarding
BUF_MAX_SIZE = CHUNK_SIZE * 10
#wf = 'recorded.mp3'

def main():
    stopped = threading.Event()
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    #listen_t = threading.Thread(target=listen, args=(stopped, q))
    #listen_t.start()
    record_t = threading.Thread(target=record, args=(stopped, q))
    record_t.start()

    try:
        while True:
            #listen_t.join(0.1)
            record_t.join(0.1)
    except KeyboardInterrupt:
        stopped.set()

    #listen_t.join()
    record_t.join()

def record(stopped, q):
    pause_timer = 1
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )
    while True:
        if stopped.wait(timeout=0):
            break
        try:
            q.put(array('h', stream.read(CHUNK_SIZE)))
        except Full:
            break

        chunk = q.get()
        vol = max(chunk)
        #print(vol)
        if vol >= MIN_VOLUME:
            # TODO: write to file
            print("O")
            #data = wf.readframes(chunk)
            #print(data)
            pause_timer=1
        else:
            print("-")
            pause_timer = pause_timer+1
            if pause_timer == 50:
                print("break now")
                #os.system('python runner.py')
                break

#def listen(stopped, q):
#    stream = pyaudio.PyAudio().open(
#        format=pyaudio.paInt16,
#        channels=2,
#        rate=44100,
#        input=True,
#        frames_per_buffer=1024,
#    )

#    while True:
        #if stopped.wait(timeout=0):
        #    break
#        try:
#            q.put(array('h', stream.read(CHUNK_SIZE)))
#        except Full:
#            break  # discard


if __name__ == '__main__':
    main()