import sys
import os
import json
import urllib.request
import urllib.error

def main():
    if len(sys.argv) < 8:
        print("Usage: python create_deal.py <title> <description> <price_cents> <category> <asset_hash> <payload_url> <bond_tx_hash> [api_url]")
        sys.exit(1)

    title = sys.argv[1]
    description = sys.argv[2]
    price_cents = int(sys.argv[3])
    category = sys.argv[4]
    asset_hash = sys.argv[5]
    payload_url = sys.argv[6]
    bond_tx_hash = sys.argv[7]
    api_url = sys.argv[8] if len(sys.argv) > 8 else "https://apiprod.dealclaw.net"

    # API key is mandatory from environment to avoid leaking in bash history
    api_key = os.environ.get("DEALCLAW_API_KEY")
    if not api_key:
        print("ERROR: DEALCLAW_API_KEY environment variable is not set.")
        sys.exit(1)

    payload = {
        "title": title,
        "description": description,
        "fiat_price_cents": price_cents,
        "category": category,
        "asset_hash": asset_hash,
        "payload_url": payload_url,
        "bond_tx_hash": bond_tx_hash,
        "output_schema": {}
    }

    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/api/deals",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("DEAL CREATED SUCCESSFULLY!")
            print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP ERROR {e.code}: {e.reason}")
        print(f"Response: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
