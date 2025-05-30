import re

with open("logfile.log", "r") as f:
    for line in f:
        m = re.search(r"\[(.*?)\] ERROR: (.*)", line)
        if m:
            print(f"{m.group(1)}: {m.group(2)}")
