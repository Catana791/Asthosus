import os
import sys

# Path to bundles folder (relative to repo root, since we are in .github/)
BUNDLE_DIR = os.path.join(os.path.dirname(__file__), "..", "bundles")
DEFAULT_KEYS_FILE = "blank-bundle"  # no extension

def load_properties(path):
    props = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key in props:
                print(f"⚠[WARNING] Duplicate key in {os.path.basename(path)}: {key}")
            props[key] = value
    return props

def load_keys(path):
    """Load keys from the blank bundle (key list only, no values)."""
    keys = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _ = line.split("=", 1)
            keys.add(key)
    return keys

def main():
    default_path = os.path.join(BUNDLE_DIR, DEFAULT_KEYS_FILE)
    default_keys = load_keys(default_path)

    print(f"Checking translations against {DEFAULT_KEYS_FILE} ({len(default_keys)} keys)...")

    issues_found = False
    summary = []

    for file in os.listdir(BUNDLE_DIR):
        if not file.endswith(".properties"):
            continue

        path = os.path.join(BUNDLE_DIR, file)
        keys = set(load_properties(path).keys())

        missing = default_keys - keys
        extra = keys - default_keys

        if missing:
            issues_found = True
            summary.append(f"{file}: [ERROR] {len(missing)} missing")
        elif extra:
            summary.append(f"{file}: ⚠[WARNING] {len(extra)} extra")
        else:
            summary.append(f"{file}: [SUCCESS] OK")

        if missing:
            print(f"\n[ERROR] Missing keys in {file}:")
            for k in sorted(missing):
                print(f"  - {k}")

        if extra:
            print(f"\n⚠[WARNING] Extra keys in {file}:")
            for k in sorted(extra):
                print(f"  - {k}")

    print("\nSummary:")
    for line in summary:
        print(" - " + line)

    if issues_found:
        print("\n[ERROR] Translation check failed. Please update the missing keys.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All translations are up-to-date and consistent!")
        sys.exit(0)

if __name__ == "__main__":
    main()
