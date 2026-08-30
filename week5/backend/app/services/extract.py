import re

_HASHTAG_PATTERN = re.compile(r"#(\w+)")


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


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
