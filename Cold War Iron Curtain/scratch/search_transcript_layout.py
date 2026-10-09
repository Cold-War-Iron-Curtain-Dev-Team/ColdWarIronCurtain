import json

log_path = r"C:\Users\New\.gemini\antigravity-ide\brain\99c075ff-ee3e-4c89-8005-87b346f9fa50\.system_generated\logs\transcript.jsonl"
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        c = str(obj.get("content", ""))
        if "non-colliding" in c or "bookmark" in c or "1955" in c:
            print(f"Step {obj.get('step_index')}:")
            for cl in c.splitlines():
                if any(k in cl for k in ["non-colliding", "bookmark", "1955", "layout"]):
                    print("  ", cl[:140])
