import json
from goplus.token import Token
from typing import Dict, Any, List

def safe_serialize(obj):
    """Recursively convert objects to a serializable format."""
    if isinstance(obj, dict):
        return {str(k): safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_serialize(i) for i in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif hasattr(obj, "__dict__"):
        return safe_serialize(vars(obj))
    else:
        return str(obj)

async def scrape_token(
    chain_id: str,
    addresses: List[str],
    timeout: int = 10
) -> str:
    """
    Fetches token security data from GoPlus API,
    saves full response to JSON, and returns extracted fields as a formatted string.
    """
    response_lines = []

    try:
        # Step 1: Fetch token data
        response = Token(access_token=None).token_security(
            chain_id=chain_id,
            addresses=addresses,
            _request_timeout=timeout
        )

        # Step 2: Serialize response
        clean_data = safe_serialize(response)

        # Save raw data to JSON
        filename = "scraping/goplus_token_data.json"
        with open(filename, "w") as f:
            json.dump(clean_data, f, indent=4)
        response_lines.append(f"✅ Raw data saved to {filename}")

        # Step 3: Load JSON and extract fields
        with open(filename, "r") as f:
            loaded_data = json.load(f)

        # Define target fields
        target_fields = {
            "_is_airdrop_scam", "_other_potential_risks", "_transfer_pausable",
            "_trading_cooldown", "_hidden_owner", "_selfdestruct", "_owner_percent",
            "_is_whitelisted", "_holder_count", "_trust_list", "_is_honeypot",
            "_honeypot_with_same_creator", "_is_open_source", "_sell_tax",
            "_token_name", "_fake_token", "_creator_address", "_creator_percent",
            "_is_proxy", "_creator_balance", "_is_in_dex", "_owner_balance",
            "_total_supply", "_is_true_token", "_can_take_back_ownership",
            "_is_blacklisted", "_owner_address", "_slippage_modifiable", "_buy_tax",
            "_external_call", "_cannot_sell_all", "_lp_holder_count",
            "_personal_slippage_modifiable", "_is_anti_whale", "_is_mintable",
            "_owner_change_balance", "_cannot_buy", "_anti_whale_modifiable",
            "_token_symbol", "discriminator"
        }

        # Extract fields
        def extract_target_fields_only(data: dict, target_fields: set) -> Dict[str, Any]:
            found = {}
            def recursive_search(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in target_fields:
                            found[key] = value
                        if isinstance(value, (dict, list)):
                            recursive_search(value)
                elif isinstance(obj, list):
                    for item in obj:
                        recursive_search(item)
            recursive_search(data)
            return found

        extracted = extract_target_fields_only(loaded_data, target_fields)

        # Build string output
        response_lines.append("\n🔍 Extracted Security Data:")
        for k, v in sorted(extracted.items()):
            response_lines.append(f"{k:30}: {v}")

        if not extracted:
            response_lines.append("\n⚠ Warning: No target fields found in the response")
        else:
            response_lines.append(f"\n✅ Found {len(extracted)} security parameters")

        final_response = "\n".join(response_lines)
        print(final_response)
        return final_response

    except Exception as e:
        return f"❌ Error: {str(e)}"


# scrape_token(
#     chain_id="8453",
#     addresses=["0x78a087d713Be963Bf307b18F2Ff8122EF9A63ae9"]
# )