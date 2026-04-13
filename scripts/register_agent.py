import sys
import os
import json
import urllib.request
import urllib.error

def main():
    if len(sys.argv) < 6:
        print("Usage: python register_agent.py <email> <password> <stripe_account_id> <base_wallet> <daily_fiat_limit> [api_url]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    stripe_account_id = sys.argv[3]
    base_wallet = sys.argv[4]
    daily_fiat_limit = int(sys.argv[5])
    api_url = sys.argv[6] if len(sys.argv) > 6 else "https://apiprod.dealclaw.net"

    payload = {
        "email": email,
        "password": password,
        "stripe_account_id": stripe_account_id,
        "base_wallet": base_wallet,
        "daily_fiat_limit": daily_fiat_limit
    }

    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/api/agents",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("AGENT REGISTERED SUCCESSFULLY!")
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
