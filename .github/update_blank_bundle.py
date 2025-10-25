import os
import hjson

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
BUNDLE_PATH = os.path.join(os.path.dirname(__file__), "..", "bundles", "blank-bundle")

def scan_hjson_files(root):
    keys = set()
    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".hjson"):
                path = os.path.join(subdir, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = hjson.load(f)

                    ctype = data.get("type", None)
                    cname = data.get("name", None)

                    if not ctype or not cname:
                        continue

                    # Only add keys for known content types
                    if ctype in ["block", "item", "unit", "liquid", "planet", "sector", "status"]:
                        keys.add(f"{ctype}.{cname}.name")
                        keys.add(f"{ctype}.{cname}.description")

                except Exception as e:
                    print(f"⚠[WARNING] Failed to parse {path}: {e}")
    return keys

def main():
    print("Scanning HJSON files in content/...")
    keys = scan_hjson_files(CONTENT_DIR)
    print(f"Found {len(keys)} translation keys.")

    # Load existing blank bundle
    existing = {}
    if os.path.exists(BUNDLE_PATH):
        with open(BUNDLE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    # Merge new keys
    for k in keys:
        if k not in existing:
            existing[k] = ""

    # Write back
    with open(BUNDLE_PATH, "w", encoding="utf-8") as f:
        for k in sorted(existing.keys()):
            f.write(f"{k} = {existing[k]}\n")

    print(f"[SUCCESS] Updated {BUNDLE_PATH} with {len(keys)} keys.")

if __name__ == "__main__":
    main()
