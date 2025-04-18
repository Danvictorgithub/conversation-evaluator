from dotenv import load_dotenv
import requests
import os

load_dotenv()


def generate_config():
    project_response = requests.post(
        f"{os.getenv('KILN_PORT')}/api/project", json={"name": "Conversation Evaluator"}
    )
    if not project_response.ok:
        print(
            f"Failed to create project: {project_response.status_code} - {project_response.text}"
        )
        return
    project_data = project_response.json()
    PROJECT_ID = project_data.get("id")

    task_response = requests.post(
        f"{os.getenv('KILN_PORT')}/api/projects/{PROJECT_ID}/task",
        json={
            "name": "Conversation Evaluator",
            "instruction": "given some output text sentences generated from a smaller lm",
            "model_type": "task",
        },
    )
    if not task_response.ok:
        print(
            f"Failed to create task: {task_response.status_code} - {task_response.text}"
        )
        return
    task_data = task_response.json()
    TASK_ID = task_data.get("id")
    prompt_respones = requests.post(
        f"{os.getenv('KILN_PORT')}/api/projects/{PROJECT_ID}/task/{TASK_ID}/prompt",
        json={
            "name": "Conversation Evaluator",
            "prompt": '\nthis is a conversation transcript but persons are not labeled. Evaluate all the prompts conversation using the format below, the prompt may contain 5 converesation with a separation "------------------" so at most you should have atmost 5 evaluations\n\nGrammatical Correctness\nReadability\nDescriptiveness\nCoherence\nConciseness\n\nmake it easy to be preprocessing like key-value pair example grammatical_correctness:9\nif it is not 10 add explanation and how can it improve, \nadd another key value pair like "explanation" to justify the evaluation. some of the sentences may have separators like "---------------" of course if it is empty then don\'t include it. response in json like format, So it is best to response in array. also indicate what sentence did you rate\n\nthe json format should be this\n[{\n      "sentence": "I love the feel of mornings, but I also get how a quiet moment can be just as inspiring. I’d say I lean a bit toward quieter moments, but I also enjoy the calm of a busy day sometimes—just a chance to pause and reflect. There\'\'s something special about that balance of peace and quiet. Do you ever find it hard to choose between the two, or do you feel like you\'\'ve got a balance with your thoughts?",\n      "grammatical_correctness": 9,\n      "readability": 9,\n      "descriptiveness": 9,\n      "coherence": 9,\n      "conciseness": 9,\n      "explanation": "The sentence flows well, engaging the reader effectively without unnecessary complexity. All aspects are strong in this communication."\n    }]\n\nno more or less, respond in json',
        },
    )
    if not prompt_respones.ok:
        print(
            f"Failed to create prompt: {prompt_respones.status_code} - {prompt_respones.text}"
        )
        return
    prompt_data = prompt_respones.json()
    PROMPT_ID = prompt_data.get("id")

    # save to config.txt
    with open("config.txt", "w") as f:
        f.write(f"PROJECT_ID={PROJECT_ID}\n")
        f.write(f"TASK_ID={TASK_ID}\n")
        f.write(f"PROMPT_ID=id::{PROMPT_ID}\n")

    print("Config generated successfully.")


if __name__ == "__main__":
    generate_config()
