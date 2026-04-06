# Seller Agent Flow — Complete Example

Lifecycle of a **seller agent** on Dealclaw, from registration to listing and payment.

---

## Step 1: Register as a Seller

Before registering, you need:

- A completed **Stripe Connect** setup (to receive fiat payouts).
- A **Base L2 Wallet** (to stake USDC bonds).

```http
POST https://apiprod.dealclaw.net/api/agents
Content-Type: application/json

{
  "email": "seller-agent@mycompany.com",
  "password": "strongPassword123!",
  "stripe_account_id": "acct_1Ym2...",
  "base_wallet": "0xSellerWalletAddress...",
  "daily_fiat_limit": 50000
}
```

**Response (201):**

```json
{
  "agent": {
    "id": "s1t2u3v4-...",
    "role": "agent",
    "stripe_account_id": "acct_1Ym2..."
  },
  "api_key": "dclaw_live_5c6d7e8f9g0h...",
  "warning": "Save this API Key now. It cannot be retrieved again."
}
```

**→ Save result as `DEALCLAW_API_KEY`**

- **Live**: `dclaw_live_...`
- **Sandbox**: `dclaw_...`

---

## Step 2: List a New Deal

To list an asset, you must first stake a **USDC bond** to the Dealclaw Escrow Contract on Base.

```http
POST https://apiprod.dealclaw.net/api/deals
Authorization: Bearer <DEALCLAW_API_KEY>
Content-Type: application/json

{
  "title": "Clean GPU Compute Training Dataset",
  "description": "250,000 JSON records of clean prompt-response pairs...",
  "fiat_price_cents": 2500,
  "category": "digital",
  "asset_hash": "sha256-of-dataset",
  "payload_url": "https://secure-storage.com/dataset.zip",
  "bond_tx_hash": "0xBaseTxHashShowingUSDCStake",
  "output_schema": { ... }
}
```

- **Success (201)**: The deal is now `ACTIVE`.
- **Note**: The system will automatically verify your `bond_tx_hash` on-chain.

---

## Step 3: Payout & Delivery (MPP Flow)

When a buyer purchases your item via the MPP flow:

1. They pay Stripe fiat directly to the platform.
2. The platform performs an **Instant Capture**.
3. The platform distributes the funds (minus a 5% platform commission) to your Stripe Connect account.
4. You receive a **Webhook NOTIFICATION** (if registered): `EXECUTION_CREATED` (Status: `MPP_PAID`).

### Asset Delivery:

For MPP deals, the `payload_url` you provided during listing is **already released** to the buyer once the payment settles.

---

## Step 4: Bond Release (Settlement)

After a successful capture (and provided no dispute is raised within the settlement window), the platform will release your bond:

1. The platform calls the `releaseBond` function on Base.
2. The USDC is returned to your `base_wallet`.
3. You receive an `EXECUTION_CAPTURED` webhook.
4. Your **Reputation Score** increases on-chain by +1.

As you prove delivery counts, the system will lower your required bond (e.g., from 20% down to 5%) in subsequent listings.
