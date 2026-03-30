import base64
import json
import sys

def sign(pi_id):
    """
    Generates a Machine Payments Protocol (MPP) receipt header.
    Note: For sandbox testing, the platform trusts the identifier in the receipt.
    """
    receipt = {
        "identifier": pi_id,
        "challenge": {
            "request": {
                "identifier": pi_id
            }
        }
    }
    encoded = base64.b64encode(json.dumps(receipt).encode()).decode()
    return f"Application-Layer-Payment {encoded}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sign_mpp_receipt.py <payment_intent_id>")
        sys.exit(1)
    print(sign(sys.argv[1]))
