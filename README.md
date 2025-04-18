# conversation-evaluator

A Python tool for evaluating conversations, designed to analyze dialogue quality, coherence, and other conversational metrics.

This repository is used for reference in thesis paper "Enhancing Language Model Efficiency through Sequence-Level Knowledge Distillation with Sparse Transformers" by Ronald John Atanoso and Dan Victor Lofranco

## Features

- Automated conversation evaluation using multiple LLMs
- Database integration for storing evaluation results
- Extensible evaluation metrics
- Batch and parallel processing

## Setup

1. **Clone the repository:**

   ```bash
   git clone git@github.com:Danvictorgithub/conversation-evaluator.git
   cd conversation-evaluator
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   - Copy `env.example` to `.env` and fill in the required values.
   - After running `gen_config.py`, copy the generated IDs from `config.txt` into your `.env` file (see `env.example` for the required keys).

4. **Generate project/task/prompt configuration:**

   ```bash
   python gen_config.py
   ```

   This will create a `config.txt` file with the necessary IDs. Copy these to your .env using .env.example as reference

5. **Run the evaluator:**
   ```bash
   python main.py
   ```

## Files

- `main.py` — Main automation script for conversation evaluation
- `gen_config.py` — Script to generate project/task/prompt configuration via API
- `db.py` — SQLAlchemy models and session setup
- `provider.py` — Conversation generation logic (user-implemented)
- `env.example` — Example environment configuration

## Notes

- The `LLM_FOLDER` variable in `.env` should point to your GPT-2 model directory, as used by the `sample.py` script from the GPT-2 repository.

## Reference

This repository is part of the implementation referenced in our thesis paper.

## License

MIT License
