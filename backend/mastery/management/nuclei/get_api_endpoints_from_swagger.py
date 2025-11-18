import yaml

FRONTEND = "https://mestring-dev.osloskolen.no"

with open("Mastery API.yaml", "r") as f:
    spec = yaml.safe_load(f)

paths = spec.get("paths", {})

with open("urls.txt", "w") as out:
    for path in paths.keys():
        out.write(f"{FRONTEND}{path}\n")

print("Wrote", len(paths), "URLs")
