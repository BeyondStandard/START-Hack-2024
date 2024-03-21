import io
import os
import subprocess
import gc

# Launch the service 
subprocess.Popen(["uvicorn", "backend.app:app","--reload","--port","8000"])
os.system('speech_to_text.py')

gc.collect()