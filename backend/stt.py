from pydub.playback import play
from pydub import AudioSegment

import progressbar
import datetime
import asyncio
import pyaudio
import array
import wave
import os


CHUNK_SIZE = 1024
MIN_VOLUME = 2600
BUF_MAX_SIZE = CHUNK_SIZE * 10
q = asyncio.Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))
stop_event = asyncio.Event()
current_time = datetime.datetime.utcnow().strftime("%Y_%m_%dT%H_%M_%SZ")
wf = wave.open(current_time + ".mp3", "wb")
wf.setnchannels(1)
wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
wf.setframerate(44100)

# Audio globals
LANG = 'swiss' if os.environ['swissVoice'] == 'true' else 'german'
FIRST_TIME = True

# Create a progress bar widget
bar = progressbar.ProgressBar(
    max_value=50000,
    widgets=[
        "Audio Level: ",
        progressbar.Bar(marker="=", left="[", right="]"),
        progressbar.Percentage(),
    ],
)


def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


async def main():
    listener_task = asyncio.create_task(listen(q))
    recorder_task = asyncio.create_task(record(q))
    await asyncio.gather(listener_task, recorder_task)


async def record(q):
    pause_timer = 1
    while not stop_event.is_set():
        chunk = await q.get()
        vol = max(chunk)
        bar.update(vol)
        if vol < MIN_VOLUME:
            pause_timer = pause_timer + 1
            if pause_timer < 100:
                continue

            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(
                None, play_mp3, f'audio/wait_{LANG}.mp3')

            print("break now")
            wf.close()
            print("Finished Recording")
            os.system(f"python STT/speech_to_text.py {str(current_time)}.mp3")
            await task
            stop_event.set()


async def listen(q):
    global FIRST_TIME

    if FIRST_TIME:
        FIRST_TIME = False
        play_mp3(f'audio/start_{LANG}.mp3')

    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )

    while not stop_event.is_set():
        try:
            data = array.array("h", stream.read(CHUNK_SIZE))
            await q.put(data)
            # Write chunk to wave file
            try:
                wf.writeframes(data.tobytes())
            except:
                # TODO
                pass
        except asyncio.queues.QueueFull:
            return  # discard


if __name__ == "__main__":
    asyncio.run(main())
