# The main.py is responsible for automating the conversation evaluation
import requests
from dotenv import load_dotenv
import json
import os
from db import Evaluation, Session
from provider import generate_conversation
import concurrent.futures
import time
import json
import re
from demjson3 import decode as demjson_decode, JSONDecodeError as DemJSONDecodeError

load_dotenv()


def evaluate_conversation(text):
    api = f"{os.getenv('KILN_PORT')}/api/projects/{os.getenv('PROJECT_ID')}/tasks/{os.getenv('TASK_ID')}/run"
    response = requests.post(
        api,
        json={
            "model_name": os.getenv("MODEL_NAME", "gpt-4o"),
            "provider": os.getenv("PROVIDER", "openrouter"),
            "plaintext_input": text,
            "ui_prompt_method": os.getenv("PROMPT_ID", "").strip(),
        },
    )
    if not response.ok:
        return {
            "error": "Failed to evaluate conversation",
            "status_code": response.status_code,
        }
    return response.json()


def get_output(response):
    return response["output"]["output"]


def json_preprocess(response_text):
    response_text = get_output(response_text)
    # Extract the JSON part from the text
    json_start = response_text.find("[")
    json_end = response_text.rfind("]") + 1
    json_data = response_text[json_start:json_end]

    # Attempt to parse the JSON string into a Python list
    try:
        parsed_json = json.loads(json_data)
        if isinstance(parsed_json, list):
            return parsed_json
        else:
            print("Error: Expected a JSON array but got something else.")
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON with standard parser:", e)

    # Attempt to auto-fix and parse the JSON using demjson3
    try:
        print("Attempting to auto-fix JSON...")
        fixed_json = demjson_decode(json_data)
        if isinstance(fixed_json, list):
            return fixed_json
        else:
            print("Error: Expected a JSON array but got something else after auto-fix.")
            return None
    except DemJSONDecodeError as e:
        print("Error auto-fixing JSON:", e)

    # As a last resort, try to clean up common issues manually
    try:
        print("Attempting manual cleanup...")
        json_data = re.sub(
            r",\s*]", "]", json_data
        )  # Remove trailing commas before closing brackets
        json_data = re.sub(
            r",\s*}", "}", json_data
        )  # Remove trailing commas before closing braces
        parsed_json = json.loads(json_data)
        if isinstance(parsed_json, list):
            return parsed_json
        else:
            print(
                "Error: Expected a JSON array but got something else after manual cleanup."
            )
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON after manual cleanup:", e)

    # If all attempts fail, return None
    print("Failed to process JSON data.")
    return None


def save_to_db(json_array, model_name, seed):
    with Session() as session:
        for json_data in json_array:
            evaluation = Evaluation(
                model_name=model_name,
                sentence=json_data["sentence"],
                grammatical_correctness=json_data["grammatical_correctness"],
                readability=json_data["readability"],
                descriptiveness=json_data["descriptiveness"],
                coherence=json_data["coherence"],
                conciseness=json_data["conciseness"],
                explanation=json_data["explanation"],
                seed=seed,
            )
            session.add(evaluation)
        session.commit()


def process_batch(model_type):
    try:
        # Generate conversation
        result = generate_conversation(model_type)
        if result is None:
            print("Failed to generate conversation. Aborting.")
            return
        conversation, seed = result  # Unpack only if result is not None
        print(f"Conversation Generated (Seed: {seed}): {conversation}")
    except Exception as e:
        print("Error generating conversation:", e)
        return

    max_retries = 3
    backoff_time = 2  # Initial backoff time in seconds
    response = None

    # Retry mechanism for evaluating conversation
    for attempt in range(max_retries):
        try:
            print(f"Evaluating conversation (Attempt {attempt + 1}/{max_retries})...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(evaluate_conversation, conversation)
                response = future.result(timeout=30)  # Timeout after 30 seconds
            print("Response: ", get_output(response))
            break  # Exit the loop if successful
        except concurrent.futures.TimeoutError:
            print(f"Timeout during evaluation (Attempt {attempt + 1}/{max_retries}).")
        except Exception as e:
            print(
                f"Error evaluating conversation (Attempt {attempt + 1}/{max_retries}): {e}"
            )

        if attempt < max_retries - 1:
            print(f"Retrying after {backoff_time} seconds...")
            time.sleep(backoff_time)  # Wait before retrying
            backoff_time *= 2  # Exponentially increase the backoff time
        else:
            print("Max retries reached. Aborting.")
            return

    if response is None:  # Ensure response is valid before proceeding
        print("No valid response generated. Aborting.")
        return

    # Retry mechanism for JSON preprocessing
    for attempt in range(max_retries):
        try:
            json_data = json_preprocess(response)
            print("JSON Data: ", json_data)
            if json_data:
                save_to_db(json_data, model_type, seed)
                print("Data saved to database successfully.")
                return
            else:
                print("Failed to process JSON data.")
        except Exception as e:
            print(
                f"Error in JSON preprocessing (Attempt {attempt + 1}/{max_retries}): {e}"
            )

        # Generate a new response if JSON preprocessing fails
        try:
            print(f"Generating a new response (Attempt {attempt + 1}/{max_retries})...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(evaluate_conversation, conversation)
                response = future.result(timeout=30)  # Timeout after 30 seconds
            print("New Response: ", get_output(response))
        except concurrent.futures.TimeoutError:
            print(
                f"Timeout during new response generation (Attempt {attempt + 1}/{max_retries})."
            )
        except Exception as e:
            print(
                f"Error generating new response (Attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt == max_retries - 1:
                print("Max retries reached for JSON preprocessing. Aborting.")
                return


def process_model_type_once(model_type):
    print(f"Processing batch for model type: {model_type}")
    process_batch(model_type)
    time.sleep(1)  # Optional: Add a delay to avoid overwhelming the system


def main():
    model_types = [
        "out-full-wfull-54M-r5",  # Full Attention
        "out-local-w2-54M-r15",  # Local Attention
        "out-local-w16-54M-r11",
        "out-local-w32-54M-r10",
        "out-local-w64-54M-r9",
        "out-local-w128-54M-r8",
        "out-slide-w2-54M-r10",  # Sliding Window Attention
        "out-slide-w16-54M-r5",
        "out-slide-w32-54M-r6",
        "out-slide-w64-54M-r7",
        "out-slide-w128-54M-r9",
    ]

    batch_size = 1  # Number of processes to run in parallel
    while True:
        for i in range(0, len(model_types), batch_size):
            batch = model_types[i : i + batch_size]
            print(f"Processing batch: {batch}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(process_model_type_once, batch)


if __name__ == "__main__":
    main()
