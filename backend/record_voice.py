import struct
import time
import wave
from queue import Queue, Full
import pyaudio


def record(outputFile):
    # defining audio variables
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    #Y = 100
    MIN_VOLUME = 2600
    BUF_MAX_SIZE = CHUNK_SIZE * 10
    # Calling pyadio module and starting recording
    p = pyaudio.PyAudio()

    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    stream.start_stream()
    print("Starting!")

    # Recording data until under threshold
    frames = []

    pause_timer = 1

    while True:
        chunk = q.get()
        vol = max(chunk)
        # Converting chunk data into integers
        data = stream.read(chunk)
        #data_int = struct.unpack(str(2 * chunk) + "B", data)
        # Finding average intensity per chunk
        #avg_data = sum(data_int) / len(data_int)
        vol = max(chunk)
        #print(str(avg_data))
        print(vol)
        # Recording chunk data
        frames.append(data)
        #if avg_data < Y:
        if vol >=MIN_VOLUME:
            pause_timer=pause_timer+1
            if pause_timer>50:
                break
        
        else:
            print("Recording...")

    # Stopping recording
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Ending recording!")

    # Saving file with wave module
    wf = wave.open(outputFile, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


record("recorded.mp3")
