def map_priority(token: str, priority_map: dict, default="Medium"):
    token = (token or "").lower()
    return priority_map.get(token, {
        "p0":"Highest","p1":"High","p2":"Medium","p3":"Low",
        "critical":"Highest","high":"High","medium":"Medium","low":"Low",
        "sev1":"Highest","sev2":"High","sev3":"Medium","sev4":"Low",
    }.get(token, default))
