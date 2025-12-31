import os, sys, json, time, argparse
from datetime import datetime, timezone
from dotenv import load_dotenv
import tweepy
from mastodon import Mastodon
from atproto import Client

# --- MANDATE: Absolute Path to Credentials ---
DOTENV_PATH = "/home/kuro/data/.env"
load_dotenv(DOTENV_PATH)

def log_env_vars():
    print("\n--- Loaded Environment Variables (Debug) ---", file=sys.stderr)
    print(f"X_KEY (start): {os.getenv('X_CONSUMER_KEY', 'N/A')[:4]}", file=sys.stderr)
    print(f"MASTODON_URL: {os.getenv('MASTODON_API_BASE_URL', 'N/A')}", file=sys.stderr)
    print(f"BLUESKY_HANDLE: {os.getenv('BLUESKY_HANDLE', 'N/A')}", file=sys.stderr)
    print("-------------------------------------------\n", file=sys.stderr)

def post_to_mastodon(text):
    try:
        m = Mastodon(api_base_url=os.getenv("MASTODON_API_BASE_URL"), access_token=os.getenv("MASTODON_ACCESS_TOKEN"))
        status = m.status_post(text)
        return {"platform": "mastodon", "status": "success", "url": status.url}
    except Exception as e:
        return {"platform": "mastodon", "status": "failed", "error": str(e)}

def post_to_bluesky(text):
    try:
        client = Client()
        client.login(os.getenv("BLUESKY_HANDLE"), os.getenv("BLUESKY_APP_PASSWORD"))
        post = client.send_post(text=text)
        return {"platform": "bsky", "status": "success", "url": post.uri}
    except Exception as e:
        return {"platform": "bsky", "status": "failed", "error": str(e)}

def run_preformatted_post_workflow(task_id, payload):
    results = []
    text = payload.get("final_post_text", "")
    platforms = payload.get("platforms_to_post", [])
    
    if "mastodon" in platforms:
        results.append(post_to_mastodon(text))
    if "bsky" in platforms:
        results.append(post_to_bluesky(text))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_id", required=True)
    parser.add_argument("--workflow_type", required=True)
    parser.add_argument("--payload_json_string", required=True)
    args = parser.parse_args()

    log_env_vars()
    
    raw_input = args.payload_json_string
    if raw_input == "-":
        raw_input = sys.stdin.read()
    
    data = json.loads(raw_input)
    
    # Bridge Sisyphus Superset to Lolth
    payload_data = {}
    if "distribution" in data:
        first_p = list(data["distribution"].keys())[0]
        payload_data["final_post_text"] = data["distribution"][first_p]["body"]
        mapping = {"MA": "mastodon", "BS": "bsky"}
        payload_data["platforms_to_post"] = [mapping.get(k, k.lower()) for k in data["distribution"].keys()]
    else:
        payload_data = data

    report = {
        "task_id": args.task_id,
        "results": run_preformatted_post_workflow(args.task_id, payload_data)
    }
    print(json.dumps(report, indent=2))