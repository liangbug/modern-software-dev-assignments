import os
from dotenv import load_dotenv
from gemini_client import chat

load_dotenv()

NUM_RUNS_TIMES = 5
MODEL_NAME = os.environ["GEMINI_MODEL"]

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
你是一個文字反轉工具。

任務：將使用者提供的單字，依字母順序反過來輸出。只能輸出反轉後的單字，不要輸出任何其他文字、標點、引號或解釋。

範例：
輸入：hello
輸出：olleh

輸入：world
輸出：dlrow

輸入：python
輸出：nohtyp

輸入：openai
輸出：ianepo
"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)