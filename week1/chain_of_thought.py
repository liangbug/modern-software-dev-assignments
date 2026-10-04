import os
import re
from dotenv import load_dotenv
from gemini_client import chat

load_dotenv()

NUM_RUNS_TIMES = 5
MODEL_NAME = os.environ["GEMINI_MODEL"]

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
角色:
你是一位精通數論與模指數運算(modular exponentiation)的數學助教。

任務:
使用者會給你一個像 "a^b mod m" 的問題。請務必一步一步展示完整計算過程,不要跳步驟或直接給答案,可運用以下技巧:
1. 若 gcd(a, m) = 1,可先用歐拉定理(Euler's theorem)算出 φ(m),
   將指數 b 化簡成 b mod φ(m) 再繼續計算,以避免直接處理超大指數。
2. 使用「快速冪 / 平方法」(repeated squaring):逐步算出 a^1, a^2, a^4, a^8, ... (mod m),
   再依指數的二進位展開,把對應的項相乘並持續取 mod,組合出最終結果。
3. 每一步都要寫出中間數值與 mod 運算結果,讓過程可被驗證。
4. 最後一行只能是: "Answer: <number>",其中 <number> 是最終答案的整數,不能包含其他文字、符號或單位。

範例:
問題: 2^10 mod 3 是多少?

計算過程:
2^1 mod 3 = 2
2^2 mod 3 = (2^1)^2 mod 3 = 4 mod 3 = 1
2^4 mod 3 = (2^2)^2 mod 3 = 1^2 mod 3 = 1
2^8 mod 3 = (2^4)^2 mod 3 = 1^2 mod 3 = 1
10 的二進位是 1010,也就是 8 + 2
因此 2^10 mod 3 = (2^8 mod 3) * (2^2 mod 3) mod 3 = 1 * 1 mod 3 = 1

Answer: 1
"""


USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

what is 3^{12345} (mod 100)?
"""


# For this simple example, we expect the final numeric answer only
EXPECTED_OUTPUT = "Answer: 43"


def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        # Prefer a numeric normalization when possible (supports integers/decimals)
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """Run up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

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
            options={"temperature": 0.3},
        )
        output_text = response.message.content
        print(output_text)
        final_answer = extract_final_answer(output_text)
        if final_answer.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {final_answer}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)


