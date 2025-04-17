# The main.py is responsible for automating the conversation evaluation
import requests
from dotenv import load_dotenv
import json
import os
from db import Evaluation, Session
from provider import generate_conversation_full

load_dotenv()


def evaluate_conversation(text):
    api = f"{os.getenv('KILN_PORT')}/api/projects/{os.getenv('PROJECT_ID')}/tasks/{os.getenv('TASK_ID')}/run"
    print("API URL:", api)
    response = requests.post(
        api,
        json={
            "model_name": os.getenv("MODEL_NAME"),
            "provider": os.getenv("PROVIDER"),
            "plaintext_input": text,
            "ui_prompt_method": os.getenv("PROMPT_ID"),
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

    # Parse the JSON string into a Python list
    try:
        parsed_json = json.loads(json_data)
        if isinstance(parsed_json, list):
            return parsed_json
        else:
            print("Error: Expected a JSON array but got something else.")
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None


def save_to_db(json_array, model_name):
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
            )
            session.add(evaluation)
        session.commit()


def main():
    print("result:", generate_conversation_full())
    # response = evaluate_conversation(
    #     "Person A: Hi.  Person B: Hello.  Person A: How are you.  Person B: Yes.  Person A: Ok.  Person B: Bye."
    # )
    # sample_model = "sliding-sparse"
    # json_data = json_preprocess(response)
    # if json_data:
    #     save_to_db(json_data, sample_model)
    #     print("Data saved to database successfully.")
    # else:
    #     print("Failed to process JSON data.")
    # print(json_preprocess(response))


if __name__ == "__main__":
    main()
