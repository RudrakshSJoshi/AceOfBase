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

async def wallet_finder(query, wallet_address, token_address, amt, transaction_details):
    client = AsyncGroq()  # Replace with your real key
    # Format the code with numbered lines
    formatted_transactions = format_transaction_details(transaction_details)
    print(formatted_transactions)
    # Construct the prompt based on your requirements
    user_prompt = f"""
You are acting as a **Detective Agent**, helping a user investigate a suspicious or fraudulent transaction. You are provided with the following **user query and context**:

---

### 🧾 User Query:
{query}

### 📬 Wallet Address:
{wallet_address}

### 💸 Token Address (may be empty):
{token_address} (If nothing is provided, assume data not available)

### 💰 Approximate Amount Involved:
{amt} (If nothing is provided, assume data not available)

---

You have access to a function:

```python
get_wallet_transactions(wallet_address: str, token_address: Optional[str] = None, top_n: int = 10)
Meaning of Parameters:
wallet_address → the address under investigation (user's address or a suspected one)

token_address → the specific token contract involved in the transfer (can be None to widen search)

top_n → how many recent transactions to fetch (default is 10)

🧾 Transaction Details Format

{formatted_transactions}

🧠 Your Goal:
You are only the first-stage detective agent, and your goal is not to make final conclusions, but to:

Investigate based on the query, wallet address, token, and amount.

Think deeply about what may have gone wrong (Chain of Thought / CoT).

Suggest which addresses might be suspicious and should be explored further.

Prepare the data for the next agent, who will do the full diagnosis of what really happened.

You must act like a detective — find leads, spot suspicious addresses, and flag them for deeper analysis.

🧩 Capabilities of This Agent (You):

class BaseModel:
    search_queries: list[list[str]]  # Wallets to investigate, using the get_wallet_transactions function
You must respond in the following JSON format:

{{
  "search_queries": [
    ["wallet_address", "token_address (can be empty, makes search even wider, preferred to leave empty)", "top_n (default is 10, but you will always mention it)"],
    ...
  ]
}}
🧭 Final Instructions
Think about possible scam patterns based on the input.

You may return multiple addresses to analyze (not just the main one).

Do not attempt full analysis — you're a lead-finding detective!

Help us identify which other wallet addresses might be involved or suspicious.

These addresses will be passed to the next agent for deep inspection.

The user has faced a problem, and you must ensure the bad actors are caught.

Just ensure that you don't add user's wallet addrwess to the search queries, as that would be wrong.
Also you will not add more than 3 search queries, as that would be too much.
In case of more than 3, use timestamps and amount to filter the best possible wallet addresses linked to the user's query, and only return best 3.
Go detect!
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
        response_format={"type": "json_object"},
        reasoning_format="hidden"
    )

    data = response.choices[0].message.content
    # print(data)
    return json.loads(data)