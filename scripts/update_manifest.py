#!/usr/bin/env python3
"""
Auto-discovery Manifest Updater
-------------------------------
Scans the data/ directory for any new exam JSON models and automatically updates
data/manifest_models.json so they appear in the UI dropdown and test selector.
"""

import os
import json

def update_manifest(data_dir="data"):
    if not os.path.isdir(data_dir):
        print(f"Directory '{data_dir}' does not exist.")
        return

    json_files = sorted([
        f for f in os.listdir(data_dir)
        if f.endswith(".json") and f not in ["manifest_models.json", "schema_telc_b1.json"]
    ])

    manifest = []
    for idx, fname in enumerate(json_files, 1):
        fpath = os.path.join(data_dir, fname)
        model_id = os.path.splitext(fname)[0]
        title = model_id.upper()
        
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                title = data.get("title", title)
        except Exception as e:
            print(f"Warning: Could not read title from {fname}: {e}")

        manifest.append({
            "id": model_id,
            "number": idx,
            "title": title,
            "file": f"data/{fname}",
            "is_available": True
        })

    manifest_path = os.path.join(data_dir, "manifest_models.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Successfully updated {manifest_path} with {len(manifest)} models:")
    for m in manifest:
        print(f"    • [{m['number']}] {m['title']} ({m['id']}) -> {m['file']}")
    print()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update data/manifest_models.json with all test models in data/")
    parser.add_argument("--data-dir", default="data", help="Path to data directory (default: data)")
    args = parser.parse_args()
    update_manifest(args.data_dir)
