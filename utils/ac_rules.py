import re
GWT_LINE = re.compile(r"^(given|when|then|and)\b[:\-\s]*(.+)$", re.I)

def normalize_ac(lines):
    out, cur = [], []
    for ln in lines:
        t = ln.strip()
        if not t:
            if cur:
                out.append(" ".join(cur))
                cur=[]
            continue
        m = GWT_LINE.match(t)
        if m:
            role = m.group(1).title()
            rest = m.group(2).strip()
            cur.append(f"{role}: {rest}")
        else:
            cur.append(t)
    if cur: out.append(" ".join(cur))
    # de-dupe
    seen, final = set(), []
    for x in out:
        k = x.lower()
        if len(k)>3 and k not in seen:
            final.append(x)
            seen.add(k)
    return final
