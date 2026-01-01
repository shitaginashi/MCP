import yaml
import os
from mastodon import Mastodon
from atproto import Client

# --- THE VAULT BRIDGE ---
def load_vault(vault_path="api_credentials.yml"):
    if not os.path.exists(vault_path):
        print(f"❌ Error: {vault_path} not found!")
        return False
    with open(vault_path, 'r') as f:
        creds = yaml.safe_load(f)
        for k, v in creds.items():
            os.environ[k] = str(v)
    print("🔓 Vault loaded into environment.")
    return True

def verify_combat_readiness():
    if not load_vault():
        return
    
    print("🛡️ Testing Regenerated Credentials...")

    # Test Mastodon
    try:
        m = Mastodon(
            access_token=os.getenv("MASTODON_ACCESS_TOKEN"), 
            api_base_url=os.getenv("MASTODON_API_BASE_URL")
        )
        user = m.account_verify_credentials()
        print(f"🐘 Mastodon: SUCCESS (Verified as @{user['username']})")
    except Exception as e:
        print(f"❌ Mastodon: FAIL - {e}")

    # Test Bluesky
    try:
        client = Client()
        client.login(os.getenv("BLUESKY_HANDLE"), os.getenv("BLUESKY_APP_PASSWORD"))
        print(f"🦋 Bluesky: SUCCESS (Verified as {os.getenv('BLUESKY_HANDLE')})")
    except Exception as e:
        print(f"❌ Bluesky: FAIL - {e}")

if __name__ == "__main__":
    verify_combat_readiness()

print(f"DEBUG: Using Handle -> {os.getenv('BLUESKY_HANDLE')}")
print(f"DEBUG: Using Mastodon URL -> {os.getenv('MASTODON_API_BASE_URL')}")