import io
import os
import subprocess
import gc
from dotenv import load_dotenv

load_dotenv()

# Launch the service 
subprocess.Popen(["uvicorn", "backend.app:app","--reload","--port","8000"])
os.system('python backend/speech_to_text_faster.py')

gc.collect()