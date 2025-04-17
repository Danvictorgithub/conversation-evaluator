# check if the model types are runnable in your system
from provider import generate_conversation

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

runnable_models = {}

for model_type in model_types:
    print(f"Checking model type: {model_type}")
    try:
        conversation = generate_conversation(model_type)
        if conversation:
            print(f"Model type '{model_type}' is runnable.")
            print(f"Generated Conversation: {conversation}")
            runnable_models[model_type] = conversation
        else:
            print(f"Model type '{model_type}' failed to generate a conversation.")
    except Exception as e:
        print(f"Error with model type '{model_type}': {e}")

print("\nRunnable model types and their generated conversations:")
for model, conversation in runnable_models.items():
    print(f"Model: {model}")
    print(f"Conversation: {conversation}")
    print("-" * 40)
