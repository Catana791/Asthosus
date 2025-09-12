import os
from pathlib import Path
import hjson
from collections import OrderedDict

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BUNDLE_PATH = REPO_ROOT / "bundles" / "blank-bundle"

PROTECTED_START = "### NO-OVERRIDE-START ###"
PROTECTED_END = "### NO-OVERRIDE-END ###"

ALLOWED_TYPES = {"block", "item", "unit", "liquid", "planet", "sector", "status"}


def scan_hjson_files(root: Path):
    keys = set()
    if not root.exists() or not root.is_dir():
        return keys

    files = list(root.rglob("*.hjson"))
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = hjson.load(f)
            if not isinstance(data, dict):
                continue
            ctype = data.get("type")
            cname = data.get("name")
            if not ctype or not cname:
                continue
            if ctype in ALLOWED_TYPES:
                keys.add(f"{ctype}.{cname}.name")
                keys.add(f"{ctype}.{cname}.description")
        except Exception:
            continue
    return keys


def load_existing_keys(bundle_path: Path):
    existing = OrderedDict()
    protected_lines = []
    if not bundle_path.exists():
        return existing, protected_lines

    in_protected = False
    with bundle_path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped == PROTECTED_START:
                in_protected = True
                protected_lines.append(line)
                continue
            if in_protected:
                protected_lines.append(line)
                if stripped == PROTECTED_END:
                    in_protected = False
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()
    return existing, protected_lines


def write_bundle(existing_dict: dict, protected_lines: list, bundle_path: Path):
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with bundle_path.open("w", encoding="utf-8") as f:
        for k in sorted(existing_dict.keys()):
            f.write(f"{k} = {existing_dict[k]}\n")
        if protected_lines:
            f.write("\n")
            for pline in protected_lines:
                f.write(f"{pline}\n")


def main():
    scanned_keys = scan_hjson_files(CONTENT_DIR)
    existing, protected_lines = load_existing_keys(BUNDLE_PATH)
    for k in scanned_keys:
        if k not in existing:
            existing[k] = ""
    write_bundle(existing, protected_lines, BUNDLE_PATH)


if __name__ == "__main__":
    main()
