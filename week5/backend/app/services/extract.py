import re

_HASHTAG_PATTERN = re.compile(r"#(\w+)")
_CHECKBOX_PATTERN = re.compile(r"^\[\s?\]\s*(.+)$")


def extract_action_items(text: str) -> list[str]:
    """Extract action items from text.

    Recognizes two line formats:
    - Checkbox tasks: "- [ ] task text" -> "task text"
    - Legacy markers: lines ending in "!" or starting with "todo:"
    """
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    items: list[str] = []
    for line in lines:
        checkbox_match = _CHECKBOX_PATTERN.match(line)
        if checkbox_match:
            task_text = checkbox_match.group(1).strip()
            if task_text:
                items.append(task_text)
        elif line.endswith("!") or line.lower().startswith("todo:"):
            items.append(line)
    return items


def extract_hashtags(text: str) -> list[str]:
    """Extract unique #hashtag names from text, preserving first-seen order."""
    seen: set[str] = set()
    tags: list[str] = []
    for match in _HASHTAG_PATTERN.finditer(text):
        name = match.group(1)
        key = name.lower()
        if key not in seen:
            seen.add(key)
            tags.append(name)
    return tags
