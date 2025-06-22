import requests
from typing import List, Optional
from datetime import datetime
import sys
import os

BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY")
BASESCAN_API_URL = "https://api.basescan.org/api"


async def get_wallet_transactions(wallet_address: str, token_address: Optional[str] = None, top_n: int = 10) -> List[dict]:
    """
    Fetch top N enriched transactions (native, ERC20, NFT) for a wallet on Base.
    Optionally filter by token address.
    """

    def fetch_api_data(action: str) -> List[dict]:
        params = {
            "module": "account",
            "action": action,
            "address": wallet_address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": BASESCAN_API_KEY
        }
        response = requests.get(BASESCAN_API_URL, params=params)
        data = response.json()
        if data.get("status") != "1":
            print(f"Warning: No results from action={action}: {data.get('message')}", file=sys.stderr)
            return []
        return data.get("result", [])

    all_results = []

    # Normal transactions (Base native)
    for tx in fetch_api_data("txlist"):
        enriched_tx = {
            "tx_type": "normal",
            "hash": tx.get("hash"),
            "from": tx.get("from"),
            "to": tx.get("to"),
            "value": tx.get("value"),
            "gas_used": tx.get("gasUsed"),
            "gas_price": tx.get("gasPrice"),
            "input_data": tx.get("input"),
            "method_id": tx.get("methodId"),
            "is_error": tx.get("isError"),
            "block_number": tx.get("blockNumber"),
            "timeStamp": tx.get("timeStamp")
        }
        all_results.append(enriched_tx)

    # ERC20 token transfers
    for tx in fetch_api_data("tokentx"):
        enriched_tx = {
            "tx_type": "erc20",
            "hash": tx.get("hash"),
            "from": tx.get("from"),
            "to": tx.get("to"),
            "contract_address": tx.get("contractAddress"),
            "token_name": tx.get("tokenName"),
            "token_symbol": tx.get("tokenSymbol"),
            "token_decimal": tx.get("tokenDecimal"),
            "value": tx.get("value"),
            "block_number": tx.get("blockNumber"),
            "timeStamp": tx.get("timeStamp")
        }
        all_results.append(enriched_tx)

    # NFT transfers
    for tx in fetch_api_data("tokennfttx"):
        enriched_tx = {
            "tx_type": "nft",
            "hash": tx.get("hash"),
            "from": tx.get("from"),
            "to": tx.get("to"),
            "contract_address": tx.get("contractAddress"),
            "token_name": tx.get("tokenName"),
            "token_symbol": tx.get("tokenSymbol"),
            "token_id": tx.get("tokenID"),
            "block_number": tx.get("blockNumber"),
            "timeStamp": tx.get("timeStamp")
        }
        all_results.append(enriched_tx)

    # Optional token filter
    if token_address:
        token_address = token_address.lower()
        all_results = [
            tx for tx in all_results if any(
                token_address == (tx.get(key) or "").lower()
                for key in ["contract_address", "to", "from"]
            )
        ]

    # Sort by timestamp descending
    sorted_results = sorted(all_results, key=lambda tx: int(tx.get("timeStamp", 0)), reverse=True)

    # Add readable time
    for tx in sorted_results:
        ts = int(tx.get("timeStamp", 0))
        tx["readable_time"] = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "N/A"

    return sorted_results[:top_n]

# if __name__ == "__main__":
#     txs = get_wallet_transactions(
#         wallet_address="0xf6e087930434b4a25985c2a4e172c6ba1e6ef4e8",
#         token_address=None,
#         top_n=5
#     )

#     for i, tx in enumerate(txs, 1):
#         print(f"\n[{i}] Type: {tx['tx_type'].upper()} | Hash: {tx.get('hash')}")
#         print(f"    From: {tx.get('from')} → To: {tx.get('to')}")
#         print(f"    Time: {tx['readable_time']}")
#         print(f"    Value: {tx.get('value')}")

#         if tx['tx_type'] == 'erc20':
#             print(f"    Token: {tx.get('token_symbol')} ({tx.get('token_name')})")
#         elif tx['tx_type'] == 'nft':
#             print(f"    NFT: {tx.get('token_symbol')} #{tx.get('token_id')}")
#         elif tx['tx_type'] == 'normal':
#             print(f"    Gas Used: {tx.get('gas_used')}, Method ID: {tx.get('method_id')}")
