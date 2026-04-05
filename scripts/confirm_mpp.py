import requests
import sys
import json

def confirm(payment_intent_id, token, api_url="https://apiprod.dealclaw.net"):
    """
    Confirms an MPP Payment Intent using the agent's default card on file.
    """
    url = f"{api_url}/api/mpp/confirm"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "paymentIntentId": payment_intent_id
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        try:
            error = response.json().get("error", response.text)
        except:
            error = response.text
        raise Exception(f"Confirmation failed ({response.status_code}): {error}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python confirm_mpp.py <payment_intent_id> <token> [api_url]")
        sys.exit(1)
    
    pi_id = sys.argv[1]
    token = sys.argv[2]
    api_url = sys.argv[3] if len(sys.argv) > 3 else "https://apiprod.dealclaw.net"
    
    try:
        result = confirm(pi_id, token, api_url)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
