import re
WHITESPACE_RE = re.compile(r"[ \t]+")

def squash_spaces(s: str) -> str:
    return WHITESPACE_RE.sub(" ", s.strip())

def clamp_text(s: str, max_chars: int) -> str:
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "\n\n[...truncated...]"

def split_lines(s: str):
    return [ln.rstrip() for ln in s.splitlines()]
