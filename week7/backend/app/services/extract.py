import re

_PREFIX_KEYWORDS = (
    "todo:",
    "action:",
    "task:",
    "fixme:",
    "follow up:",
    "followup:",
)

_IMPERATIVE_VERBS = (
    "call",
    "email",
    "send",
    "review",
    "fix",
    "update",
    "schedule",
    "contact",
    "finish",
    "complete",
    "prepare",
    "draft",
    "follow up",
    "remember to",
    "need to",
    "needs to",
    "must",
)

_CHECKBOX_RE = re.compile(r"^\[( |x|X)\]\s*(.+)$")
_NUMBERED_RE = re.compile(r"^\d+[.)]\s*(.+)$")
_MENTION_RE = re.compile(r"@\w+")


def _strip_bullet(line: str) -> str:
    return line.lstrip("-*• ").strip()


def extract_action_items(text: str) -> list[str]:
    lines = [_strip_bullet(line) for line in text.splitlines() if line.strip()]

    results: list[str] = []
    seen: set[str] = set()

    def add(item: str) -> None:
        normalized = item.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            results.append(normalized)

    for line in lines:
        checkbox_match = _CHECKBOX_RE.match(line)
        if checkbox_match:
            checked, body = checkbox_match.groups()
            if checked.strip().lower() != "x":
                add(body)
            continue

        numbered_match = _NUMBERED_RE.match(line)
        candidate = numbered_match.group(1) if numbered_match else line
        candidate_normalized = candidate.lower()

        if any(candidate_normalized.startswith(prefix) for prefix in _PREFIX_KEYWORDS):
            add(candidate)
        elif candidate.endswith("!"):
            add(candidate)
        elif _MENTION_RE.search(candidate):
            add(candidate)
        elif any(candidate_normalized.startswith(verb) for verb in _IMPERATIVE_VERBS):
            add(candidate)
        elif numbered_match:
            add(candidate)

    return results
