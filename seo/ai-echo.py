import json
import os

def echo_library():
    # Using the correct filename we just discovered
    library_path = os.path.expanduser("~/data/sisyphus_feed.jsonl")
    
    if not os.path.exists(library_path):
        print(f"❌ File not found at {library_path}")
        return

    print(f"📜 Sisyphus is reading the scrolls...\n")
    with open(library_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                # Map the keys: 'src' for source, 'text' for content
                source = data.get('src', 'Unknown')
                content = data.get('text', 'No Intel Found')
                
                # Clean up HTML tags if they exist
                clean_content = content.replace('<p>', '').replace('</p>', ' ').strip()
                
                print(f"📍 SOURCE: {source.upper()}")
                print(f"💡 INTEL: {clean_content[:100]}...")
                print("-" * 30)
            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    echo_library()
