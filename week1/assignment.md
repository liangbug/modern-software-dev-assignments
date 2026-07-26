# Week 1 — Prompting Techniques

You will practice multiple prompting techniques by crafting prompts to complete specific tasks. Each task’s instructions are at the top of its corresponding source file.

## Installation
Make sure you have first done the installation described in the top-level `README.md`. 

## Gemini API setup
These scripts call Google's Gemini API via the `google-genai` SDK instead of running a model locally.

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Add it to a `.env` file at the project root:
   ```bash
   GEMINI_API_KEY=your-key-here
   ```

The shared `week1/gemini_client.py` helper exposes a `chat(model, messages, options)` function that mirrors the old `ollama.chat()` interface, so the rest of each script's logic is unchanged.

## Techniques and source files
- K-shot prompting — `week1/k_shot_prompting.py`
- Chain-of-thought — `week1/chain_of_thought.py`
- Tool calling — `week1/tool_calling.py`
- Self-consistency prompting — `week1/self_consistency_prompting.py`
- RAG (Retrieval-Augmented Generation) — `week1/rag.py`
- Reflexion — `week1/reflexion.py`

## Deliverables
- Read the task description in each file.
- Design and run prompts (look for all the places labeled `TODO` in the code). That should be the only thing you have to change (i.e. don't tinker with the model). 
- Iterate to improve results until the test script passes.
- Save your final prompt(s) and output for each technique.
- Make sure to include in your submission the completed code for each prompting technique file. ***Double check that all `TODO`s have been resolved.***

## Evaluation rubric (60 pts total)
- 10 for each completed prompt across the 6 different prompting techniques