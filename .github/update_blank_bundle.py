import os
import hjson

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
BUNDLE_PATH = os.path.join(os.path.dirname(__file__), "..", "bundles", "blank-bundle")

PROTECTED_START = "### NO-OVERRIDE-START ###"
PROTECTED_END = "### NO-OVERRIDE-END ###"

def scan_hjson_files(root):
    keys = set()
    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".hjson"):
                path = os.path.join(subdir, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = hjson.load(f)

                    ctype = data.get("type")
                    cname = data.get("name")

                    if not ctype or not cname:
                        continue

                    if ctype in ["block", "item", "unit", "liquid", "planet", "sector", "status"]:
                        keys.add(f"{ctype}.{cname}.name")
                        keys.add(f"{ctype}.{cname}.description")

                except Exception as e:
                    print(f"⚠[WARNING] Failed to parse {path}: {e}")
    return keys

def read_protected_block(bundle_path):
    if not os.path.exists(bundle_path):
        return []
    lines = []
    in_block = False
    with open(bundle_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped == PROTECTED_START:
                in_block = True
            if in_block:
                lines.append(line.rstrip("\n"))
                if stripped == PROTECTED_END:
                    in_block = False
    return lines

def main():
    print("Scanning HJSON files in content/...")
    keys = scan_hjson_files(CONTENT_DIR)
    print(f"Found {len(keys)} translation keys.")

    existing = {}
    if os.path.exists(BUNDLE_PATH):
        with open(BUNDLE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    for k in keys:
        if k not in existing:
            existing[k] = ""

    protected_lines = read_protected_block(BUNDLE_PATH)

    with open(BUNDLE_PATH, "w", encoding="utf-8") as f:
        for k in sorted(existing.keys()):
            f.write(f"{k} = {existing[k]}\n")
        if protected_lines:
            f.write("\n")
            for pline in protected_lines:
                f.write(f"{pline}\n")

    print(f"[SUCCESS] Updated {BUNDLE_PATH} with {len(keys)} keys.")

if __name__ == "__main__":
    main()
