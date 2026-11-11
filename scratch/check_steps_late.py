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
        if 1250 <= obj.get("step_index", 0) <= 1275:
            print(f"=== Step {obj.get('step_index')}: {obj.get('type')} ===")
            content = obj.get("content", "")
            if content:
                print(str(content)[:1000])
