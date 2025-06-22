from groq import AsyncGroq
import asyncio
import json

from typing import List, Dict

def format_transaction_details(transaction_details) -> str:
    output = []

    for i, tx in enumerate(transaction_details, 1):
        lines = [f"[{i}] Type: {tx['tx_type'].upper()} | Hash: {tx.get('hash', 'N/A')}"]
        lines.append(f"    From: {tx.get('from', 'N/A')} → To: {tx.get('to', 'N/A')}")
        lines.append(f"    Time: {tx.get('readable_time', 'N/A')}")
        lines.append(f"    Value: {tx.get('value', 'N/A')}")

        if tx['tx_type'] == 'erc20':
            lines.append(f"    Token: {tx.get('token_symbol', 'N/A')} ({tx.get('token_name', 'N/A')})")
        elif tx['tx_type'] == 'nft':
            lines.append(f"    NFT: {tx.get('token_symbol', 'N/A')} #{tx.get('token_id', 'N/A')}")
        elif tx['tx_type'] == 'normal':
            lines.append(f"    Gas Used: {tx.get('gas_used', 'N/A')}, Method ID: {tx.get('method_id', 'N/A')}")

        output.append("\n".join(lines))

    return "\n\n".join(output)

async def fraud_analyzer(query, wallet_address, token_address, amt, transaction_details, total_transaction_details):
    client = AsyncGroq()  # Replace with your real key
    # Format the code with numbered lines
    formatted_transactions = format_transaction_details(transaction_details)
    print(formatted_transactions)
    # Construct the prompt based on your requirements
    user_prompt = f"""
You are acting as the **Deep Analysis Detective Agent**, assisting a user who suspects a fraudulent transaction involving their wallet.

You are provided with the following inputs:

---

### 🧾 User Query:
{query}

### 📬 User Wallet Address:
{wallet_address}

### 💸 Token Address:
{token_address} (If empty, consider it unknown but try to estimate from the data)

### 💰 Approximate/Precise Amount Lost:
{amt} (If empty, consider it unknown but try to estimate from the data)

---

### 📂 Data Provided to You:

1. **User Transaction Details**
   - These are transactions where the user’s wallet sent or received funds.
   - Use this to identify **initial fund outflow** and possible **entry points** for the fraud.

```python
transaction_details = {formatted_transactions}
````

2. **Total Transaction Details**

   * These are transactions involving **wallets suspected by the first-stage agent**.
   * Use this to trace how the funds might have flowed after leaving the user.

```python
total_transaction_details = {total_transaction_details}
```

---

### 🎯 Your Mission:

You must generate a **final report-style analysis as a string** (do not return JSON, Markdown, or code blocks).

Structure your response with clear sections using ALL CAPS HEADERS (like `INITIAL ANALYSIS`, `MONEY FLOW TRACE`, etc.).

Think like a blockchain forensic analyst. Your response must be methodical, insightful, and clear.

---

### 🧠 Chain of Thought You Must Follow:

1. **INITIAL ANALYSIS**

   * Start from the user's transaction details.
   * Identify transactions where funds exited the user’s wallet.
   * List recipient address, value transferred, and timestamp.
   * Flag any suspicious patterns (e.g., unusual approvals, token transfers to unknown wallets).

2. **MONEY FLOW TRACE**

   * Use the total\_transaction\_details to track where the money went after it left the user.
   * Map the transfer chain:
     USER WALLET → WALLET A → WALLET B → FINAL WALLET or DEX
   * Distinguish between:

     * **Intermediate Wallets**: Only forward funds
     * **Likely Final Wallets**: Hold funds or dump them via DEX/CEX
   * Mention:

     * Time of transfer
     * Value
     * Wallet addresses involved

3. **SCENARIO ANALYSIS**

   * Based on the flow, deduce the most probable scam scenario.
   * Common examples:

     * Phishing attack
     * Fake approval transaction
     * Token swap scam
     * Interaction with a malicious contract
   * Keep tone neutral but informative, label clearly what is "likely", "confirmed", or "uncertain".

4. **FUND RECOVERY POTENTIAL**

   * Determine if the funds are still in an address or sent to a DEX, bridge, or mixer.
   * If recoverable (e.g., held in a known address or paused smart contract), explain how.
   * If unrecoverable (e.g., laundered or bridged), state so.
   * Mention any signs of hope or concern.

5. **WALLET REPORT UPDATES**
   End with a question to the user:

   > Would you like me to flag these suspicious accounts and ensure they are permanently blocked from interacting with your wallet or any connected addresses?
   > I can also generate a formal report for these potentially malicious wallets to be submitted for further investigation.

---

### 🛑 IMPORTANT INSTRUCTIONS

* DO NOT return JSON or structured data.
* DO NOT call or refer to any functions.
* DO NOT use markdown or code formatting.
* Return a single, clean, readable **string output**, structured like a human analyst's written report.

Be precise, comprehensive, and helpful. The user is relying on you for clarity and insight.
"""
    # print(formatted_code)
    response = await client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        reasoning_format="hidden"
    )

    data = response.choices[0].message.content
    # print(data)
    return data