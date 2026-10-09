import json

log_path = r"C:\Users\New\.gemini\antigravity-ide\brain\99c075ff-ee3e-4c89-8005-87b346f9fa50\.system_generated\logs\transcript.jsonl"
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "MLA_Show_the_Malay_a_Better_Future" in line:
            obj = json.loads(line)
            idx = obj.get("step_index")
            t = obj.get("type")
            print(f"Step {idx}: {t}")
            content = str(obj.get("content", ""))
            for c_line in content.splitlines():
                if "MLA_Show_the_Malay_a_Better_Future" in c_line:
                    print("   ", c_line[:140])
