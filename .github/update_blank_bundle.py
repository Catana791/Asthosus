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

                    ctype = data.get("type", None)
                    cname = data.get("name", None)

                    if not ctype or not cname:
                        continue

                    # Only add keys for known content types
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

                # Only parse key=value pairs outside the protected block
                if not in_protected and "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    return existing, protected_lines

def write_bundle(keys, protected_lines, bundle_path):
    with open(bundle_path, "w", encoding="utf-8") as f:
        # write sorted generated keys
        for k in sorted(keys.keys()):
            f.write(f"{k} = {keys[k]}\n")

        f.write("\n")

        # re-add preserved block if it exists
        if protected_lines:
            f.write("\n".join(protected_lines))
            f.write("\n")

def main():
    print("Scanning HJSON files in content/...")
    keys = scan_hjson_files(CONTENT_DIR)
    print(f"Found {len(keys)} translation keys in content/.")

    existing, protected_lines = load_existing_keys(BUNDLE_PATH)

    # Merge new keys into existing ones (outside protected block)
    for k in keys:
        if k not in existing:
            existing[k] = ""

    write_bundle(existing, protected_lines, BUNDLE_PATH)

    print(
        f"[SUCCESS] Updated {BUNDLE_PATH} with {len(existing)} generated keys "
        f"(plus preserved block of {len(protected_lines)} lines)."
    )

if __name__ == "__main__":
    main()
