import sys
import hashlib
import requests
import json
import os

def verify_and_dispute(execution_id, payload_url, expected_hash, dealclaw_token, output_schema=None):
    """
    Downloads an asset, verifies its SHA-256 hash (streamed for large files),
    validates its schema (if provided), and automatically raises a dispute
    on the Dealclaw platform if verification fails.
    """
    print(f"[*] Starting verification for execution {execution_id}...")
    print(f"[*] Downloading from {payload_url}...")

    sha256 = hashlib.sha256()
    
    try:
        # 1. Streamed Download & Hash Computation
        with requests.get(payload_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    sha256.update(chunk)
        
        actual_hash = sha256.hexdigest()
        print(f"[*] Actual Hash:   {actual_hash}")
        print(f"[*] Expected Hash: {expected_hash}")

        # 2. Hash Verification
        if actual_hash != expected_hash:
            print("[!] HASH MISMATCH DETECTED!")
            return raise_dispute(execution_id, dealclaw_token, f"Hash mismatch. Expected {expected_hash}, got {actual_hash}", actual_hash)

        # 3. Optional Schema Validation (if it's a JSON asset)
        if output_schema:
            print("[*] Validating output schema...")
            try:
                # Re-download for schema check (or optimize to check first chunk if possible)
                # For simplicity in this script, we fetch the full content for validation
                data_resp = requests.get(payload_url, timeout=10)
                data = data_resp.json()
                
                import jsonschema
                jsonschema.validate(instance=data, schema=output_schema)
                print("[+] Schema validation passed.")
            except Exception as e:
                print(f"[!] SCHEMA VALIDATION FAILED: {str(e)}")
                return raise_dispute(execution_id, dealclaw_token, f"Schema validation failed: {str(e)}", actual_hash)

        print("[+ ] Verification successful. No dispute needed.")
        return {"status": "verified", "hash": actual_hash}

    except Exception as e:
        print(f"[!] Error during verification: {str(e)}")
        # We don't auto-dispute network errors, only content errors.
        return {"status": "error", "message": str(e)}

def raise_dispute(execution_id, token, reason, proof_hash):
    """
    Private helper to trigger the Dealclaw dispute API.
    """
    api_url = os.environ.get("DEALCLAW_API_BASE", "https://apiprod.dealclaw.net")
    url = f"{api_url}/api/executions/{execution_id}/dispute"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "reason": reason,
        "proof_hash": proof_hash
    }
    
    print(f"[*] Raising dispute: {reason}")
    resp = requests.post(url, headers=headers, json=payload)
    
    if resp.status_code == 200:
        print("[+] Dispute raised successfully. Asset is now in 'DISPUTED' state.")
        return {"status": "disputed", "reason": reason, "proof_hash": proof_hash}
    else:
        print(f"[!] Failed to raise dispute: {resp.status_code} - {resp.text}")
        return {"status": "dispute_failed", "error": resp.text}

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python verify_delivery.py <execution_id> <payload_url> <expected_hash> <DEALCLAW_TOKEN> [output_schema_json]")
        sys.exit(1)

    exec_id = sys.argv[1]
    url = sys.argv[2]
    expected = sys.argv[3]
    token = sys.argv[4]
    schema = None
    
    if len(sys.argv) > 5:
        try:
            schema = json.loads(sys.argv[5])
        except:
            print("[!] Warning: Could not parse output_schema_json. Skipping schema validation.")

    result = verify_and_dispute(exec_id, url, expected, token, schema)
    print(json.dumps(result, indent=2))
