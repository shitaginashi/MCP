import os
import sys
import json
import yaml
import argparse
from datetime import datetime

# --- SYSTEM MANDATES: ABSOLUTE PATHS ---
DATA_DIR = "/home/kuro/data"
BRANDING_PATH = os.path.join(DATA_DIR, "dsop_branding_v1.yml")
RAW_FEED_PATH = os.path.join(DATA_DIR, "sisyphus_feed.jsonl")
LIBRARY_PATH = os.path.join(DATA_DIR, "library.yml")

class SisyphusMark3:
    def __init__(self):
        self._check_paths()
        with open(BRANDING_PATH, 'r', encoding='utf-8') as f:
            self.branding = yaml.safe_load(f)
        self.persona = self.branding.get('brand_identity', {})
        self.seo = self.branding.get('seo_and_platform_guidelines', {})

    def _check_paths(self):
        if not os.path.exists(BRANDING_PATH):
            print(f"CRITICAL ERROR: Branding not found at {BRANDING_PATH}", file=sys.stderr)
            sys.exit(1)

    def refine_intel(self):
        """Moves raw JSONL entries into the permanent YAML library."""
        if not os.path.exists(RAW_FEED_PATH):
            print("DEBUG: No raw feed found to refine.", file=sys.stderr)
            return

        with open(RAW_FEED_PATH, 'r', encoding='utf-8') as f:
            raw_items = [json.loads(line) for line in f]

        library = []
        if os.path.exists(LIBRARY_PATH):
            with open(LIBRARY_PATH, 'r', encoding='utf-8') as f:
                library = yaml.safe_load(f) or []

        for item in raw_items:
            library.append({
                'origin': item.get('src', 'unknown'),
                'text': item.get('text', ''),
                'refined_at': datetime.now().isoformat()
            })

        with open(LIBRARY_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(library, f, default_flow_style=False)
        print(f"SUCCESS: {len(raw_items)} items refined into {LIBRARY_PATH}", file=sys.stderr)

    def get_harvest(self):
        """Pulls the latest entry from the YAML library."""
        if not os.path.exists(LIBRARY_PATH):
            return "Library is empty. Run --refine first."
        with open(LIBRARY_PATH, 'r', encoding='utf-8') as f:
            library = yaml.safe_load(f)
            if library and len(library) > 0:
                return library[-1].get('text')
            return "No entries found in YAML library."

    def generate_superset(self, content, platforms, schedule=None):
        """Generates the Master JSON for Lolth."""
        motto = self.persona.get('motto', "")
        branded_text = f"{content}\n\n{motto}".strip()
        
        superset = {
            "meta": {
                "agent": "Sisyphus-M3",
                "timestamp": datetime.now().isoformat(),
                "scheduled_at": schedule or "instant"
            },
            "distribution": {}
        }

        for p in platforms:
            p = p.upper()
            superset["distribution"][p] = {
                "body": branded_text,
                "tags": self.seo.get('hashtags', {}).get('primary', [])[:5]
            }
        return superset

# --- EXECUTION BLOCK ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mark 3 Sisyphus Agency Agent")
    parser.add_argument('--raw', type=str, help="Direct text input")
    parser.add_argument('--harvest', action='store_true', help="Pull from YAML library")
    parser.add_argument('--refine', action='store_true', help="Refine raw JSONL into YAML library")
    parser.add_argument('-MA', action='store_true', help="Route to Mastodon")
    parser.add_argument('-BS', action='store_true', help="Route to BlueSky")
    parser.add_argument('--dry-run', action='store_true', help="Output JSON to stdout")
    
    args = parser.parse_args()
    sisyphus = SisyphusMark3()

    if args.refine:
        sisyphus.refine_intel()

    content = ""
    if args.raw:
        content = args.raw
    elif args.harvest:
        content = sisyphus.get_harvest()

    platforms = []
    if args.MA: platforms.append("MA")
    if args.BS: platforms.append("BS")

    if content and platforms:
        payload = sisyphus.generate_superset(content, platforms)
        if args.dry_run:
            print(json.dumps(payload, indent=4))
        else:
            print(json.dumps(payload)) # For Lolth pipe
    elif not args.refine:
        parser.print_help()