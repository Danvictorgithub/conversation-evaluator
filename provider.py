import subprocess
import random
import os
from dotenv import load_dotenv

load_dotenv()


def generate_conversation_full():
    seed = random.randint(0, 1000000)
    llm_folder = os.getenv("LLM_FOLDER", "")
    command = f"python sample_gen.py --out_dir=out-full-wfull-54M-r5 --seed={seed}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            cwd=llm_folder,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return None
