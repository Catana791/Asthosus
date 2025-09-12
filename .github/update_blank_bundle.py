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
                    print(f"⚠ [WARNING] Failed to parse {path}: {e}")
    return keys


def load_existing_keys(bundle_path):
    existing = {}
    protected_lines = []
    in_protected = False

    if os.path.exists(bundle_path):
        with open(bundle_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()

                if stripped == PROTECTED_START:
                    in_protected = True
                if in_protected:
                    protected_lines.append(line.rstrip("\n"))
                if stripped == PROTECTED_END:
                    in_protected = False
                    continue  # don’t parse line as key=value

                if not in_protected and "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    return existing, protected_lines


def write_bundle(keys, protected_lines, bundle_path):
    with open(bundle_path, "w", encoding="utf-8") as f:
        for k in sorted(keys.keys()):
            f.write(f"{k} = {keys[k]}\n")

        if protected_lines:
            f.write("\n")
            f.write("\n".join(protected_lines))
            f.write("\n")


def main():
    print("Scanning HJSON files in content/...")
    scanned_keys = scan_hjson_files(CONTENT_DIR)
    print(f"   Found {len(scanned_keys)} keys from content/.")

    existing, protected_lines = load_existing_keys(BUNDLE_PATH)
    print(f"   Loaded {len(existing)} existing keys and {len(protected_lines)} protected lines.")

    # Merge scanned keys into existing
    for k in scanned_keys:
        if k not in existing:
            existing[k] = ""

    write_bundle(existing, protected_lines, BUNDLE_PATH)

    print(f"[SUCCESS] Updated {BUNDLE_PATH} with {len(existing)} generated keys "
          f"+ preserved block of {len(protected_lines)} lines.")


if __name__ == "__main__":
    main()
