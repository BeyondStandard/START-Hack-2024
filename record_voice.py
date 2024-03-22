import asyncio
import os
import wave
from array import array
from datetime import datetime
import pyaudio

CHUNK_SIZE = 1024
MIN_VOLUME = 2600
BUF_MAX_SIZE = CHUNK_SIZE * 10
q = asyncio.Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))
stop_event = asyncio.Event()
wf = wave.open(record(audio_filename), "wb")
wf.setnchannels(2)
wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
wf.setframerate(44100)


async def main():
    listener_task = asyncio.create_task(listen(q))
    recorder_task = asyncio.create_task(record(q))
    await asyncio.gather(listener_task, recorder_task)


async def record(q):
    start_timer = 1
    pause_timer = 1
    while not stop_event.is_set():
        chunk = await q.get()
        vol = max(chunk)
        if vol >= MIN_VOLUME:
            print("0")
            start_timer = start_timer+1
            if start_timer>=5:
                wf.writeframes
            pause_timer = 1
        else:
            print("-")
            pause_timer = pause_timer + 1
            if pause_timer == 50:
                print("break now")
                wf.close()
                print("Finished Recording")
                current_time = datetime.utcnow().strftime('%Y_%m_%dT%H_%M_%SZ')
                audio_filename = current_time + ".mp3"

                #os.system(f'python backend/speech_to_text.py {audio_filename}')
                #os.system('python backend/speech_to_text.py '+str(current_time)+'.mp3')
                #stop_event.set()
                return audio_filename


async def listen(q):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )

    while not stop_event.is_set():
        try:
            data = array('h', stream.read(CHUNK_SIZE))
            await q.put(data)
            # Write chunk to wave file
            try:
                wf.writeframes(data.tobytes())
            except:
                # TODO
                pass
        except asyncio.queues.QueueFull:
            return  # discard


if __name__ == '__main__':
    asyncio.run(main())