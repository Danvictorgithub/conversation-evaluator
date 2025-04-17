# check if the model types are runnable in your system
from provider import generate_conversation

model_types = [
    "out-full-wfull-54M-r5",  # Full Attention
    "out-local-w64-54M-r9",  # Local Attention
    "out-local-w2-54M-r15",
    "out-local-w4-54M-r13",
    "out-local-w16-54M-r11",
    "out-local-w32-54M-r10",
    "out-local-w64-54M-r9",
    "out-local-w128-54M-r8",
    "out-slide-w64-54M-r7",  # Sliding Window Attention
    "out-slide-w2-54M-r10",
    "out-slide-w16-54M-r5",
    "out-slide-w32-54M-r6",
    "out-slide-w64-54M-r7",
    "out-slide-w128-54M-r9",
]

runnable_models = []

for model_type in model_types:
    print(f"Checking model type: {model_type}")
    try:
        conversation = generate_conversation(model_type)
        if conversation:
            print(f"Model type '{model_type}' is runnable.")
            runnable_models.append(model_type)
        else:
            print(f"Model type '{model_type}' failed to generate a conversation.")
    except Exception as e:
        print(f"Error with model type '{model_type}': {e}")

print("\nRunnable model types:")
for model in runnable_models:
    print(model)
