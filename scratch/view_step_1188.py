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
        if obj.get("step_index") == 1188:
            print(obj["tool_calls"][0]["args"]["CommandLine"])
