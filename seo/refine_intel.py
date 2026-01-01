import json
import yaml
import os

RAW_FEED = "/home/kuro/data/sisyphus_feed.jsonl"
YAML_LIB = "/home/kuro/data/library.yml"

def refine():
    if not os.path.exists(RAW_FEED):
        return

    # 1. Read Raw JSONL
    new_items = []
    with open(RAW_FEED, 'r') as f:
        for line in f:
            new_items.append(json.loads(line))

    # 2. Load Existing YAML Library
    library = []
    if os.path.exists(YAML_LIB):
        with open(YAML_LIB, 'r') as f:
            library = yaml.safe_load(f) or []

    # 3. Merge (Avoiding duplicates by text hash if needed)
    # For now, we just append the new batch
    library.extend(new_items)

    # 4. Save back to YAML
    with open(YAML_LIB, 'w') as f:
        yaml.dump(library, f, default_flow_style=False)
    
    print(f"SUCCESS: Migrated {len(new_items)} items to {YAML_LIB}")