from typing import Tuple, List, Dict
from utils.text import split_lines, squash_spaces, clamp_text
from utils.ac_rules import normalize_ac
from utils.detection import *
from utils.mapping import map_priority

def parse_text(raw: str, project_key: str,
               default_labels: List[str],
               default_components: List[str],
               options: Dict) -> Tuple[Dict, Dict]:

    lines = split_lines(raw)
    title = ""
    labels = set([x.lower() for x in default_labels])
    components = set(default_components)
    priority = None
    story_points = None
    epic_link = None
    user_story_lines = []
    desc_lines = []
    ac_block = []
    in_ac = False

    for ln in lines:
        l = ln.strip()
        low = l.lower()

        if RE_ACCEPTANCE.match(low):
            in_ac = True
            continue

        if in_ac:
            if not l:
                in_ac = False
            else:
                ac_block.append(l)
            continue

        if not title:
            m = RE_TITLE.match(low)
            if m:
                title = m.group(2).strip()
                continue

        m = RE_LABELS.match(low)
        if m:
            labels.update(comma_words(m.group(1)))
            continue

        m = RE_COMPONENTS.match(low)
        if m:
            components.update(comma_words(m.group(1)))
            continue

        m = RE_PRIORITY.match(low)
        if m:
            priority = m.group(1).strip().lower()
            continue

        m = RE_POINTS.match(low)
        if m:
            try:
                story_points = float(m.group(2))
            except: pass
            continue

        m = RE_EPIC.match(low)
        if m:
            epic_link = m.group(2).strip()
            continue

        if RE_USER_STORY.match(low):
            user_story_lines.append(l)
        else:
            desc_lines.append(l)

        if options.get("label_hashtags", True):
            for tag in find_hashtags(l):
                labels.add(tag)

        if options.get("detect_points_from_text", True) and story_points is None:
            m = RE_POINTS_INLINE.search(l)
            if m:
                try: story_points = float(m.group(1))
                except: pass

        if options.get("detect_priority_from_text", True) and not priority:
            m = RE_PRIORITY_INLINE.search(l)
            if m:
                priority = m.group(1)

    acceptance = normalize_ac(ac_block)

    if not title:
        title = (user_story_lines[0] if user_story_lines else "")
        title = title or next((x for x in lines if x.strip()), "Generated Story")
        title = squash_spaces(title)[:255]

    desc = []
    if user_story_lines:
        desc.append("### User Story")
        desc.extend(user_story_lines)
    if desc_lines:
        desc.append("### Details / Context")
        desc.extend(desc_lines)
    if acceptance:
        desc.append("### Acceptance Criteria")
        desc.extend(f"- {a}" for a in acceptance)

    description = "\n".join(desc).strip()
    prio = map_priority(priority, options.get("priority_map", {})) if priority else None

    story = {
        "project_key": project_key,
        "summary": title,
        "description": clamp_text(description, options.get("max_chars", 400000)),
        "acceptance_criteria": acceptance,
        "labels": sorted(labels),
        "components": sorted(components),
        "story_points": story_points,
        "priority": prio,
        "epic_link": epic_link,
        "assignee_account_id": None,
    }

    diagnostics = {
        "found_user_story_lines": len(user_story_lines),
        "ac_count": len(acceptance),
        "labels_auto": sorted(list(labels)),
        "priority_token": priority,
        "story_points_detected": story_points,
    }

    return story, diagnostics
