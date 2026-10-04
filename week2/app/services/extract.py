from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from .gemini_client import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique

def extract_action_items_llm(text: str) -> List[str]:
    system_prompt = """## 角色
你是一名專門從會議記錄或任意文字中擷取待辦事項的助理。

## 任務
閱讀輸入文字，找出所有可執行的任務、TODO、下一步行動，輸出成簡潔、命令語氣的字串。
- 去除項目符號、checkbox 標記，以及 `TODO:`、`Action:` 等前綴
- 若文字中沒有任何待辦事項，輸出空陣列"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    options = {
        "temperature": 0,
        "response_mime_type": "application/json",
        "response_schema": {"type": "array", "items": {"type": "string"}},
    }
    model =  os.environ["GEMINI_MODEL"]
    response = chat(model, messages, options=options)
    content = response.message.content
    try:
        items: Any = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(items, list):
        return []
    cleaned: List[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned.append(stripped)
    return cleaned

def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
