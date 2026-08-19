import re

_TAG_PATTERN = re.compile(r"#(\w+)")


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    tags: list[str] = []
    for match in _TAG_PATTERN.finditer(text):
        tag = match.group(1).lower()
        if tag not in tags:
            tags.append(tag)
    return tags
