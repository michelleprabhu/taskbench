import re

RE_TITLE = re.compile(r"^(title|summary)\s*:\s*(.+)$", re.I)
RE_LABELS = re.compile(r"^labels?\s*:\s*(.+)$", re.I)
RE_COMPONENTS = re.compile(r"^components?\s*:\s*(.+)$", re.I)
RE_PRIORITY = re.compile(r"^priority\s*:\s*(.+)$", re.I)
RE_POINTS = re.compile(r"^(story points|sp|points)\s*:\s*([\d\.]+)$", re.I)
RE_EPIC = re.compile(r"^(epic|epic link)\s*:\s*(.+)$", re.I)
RE_USER_STORY = re.compile(r"^(as\s+an?|as\s+the).+", re.I)
RE_ACCEPTANCE = re.compile(r"^(acceptance criteria|ac|criteria)\s*:\s*$", re.I)

RE_POINTS_INLINE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(story\s*points?|points?)\b", re.I)
RE_PRIORITY_INLINE = re.compile(r"\b(p0|p1|p2|p3|sev[1-4]|critical|high|medium|low)\b", re.I)
RE_HASHTAG = re.compile(r"(?:^|\s)#([a-z0-9_\-]+)")

def comma_words(val: str):
    return [x.strip() for x in val.split(",") if x.strip()]

def find_hashtags(line: str):
    return [m.group(1).lower() for m in RE_HASHTAG.finditer(line)]
