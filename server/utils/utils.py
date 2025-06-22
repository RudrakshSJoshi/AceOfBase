from scraping.scrape_transactions import get_wallet_transactions

async def fetch_all_wallet_data(search_queries):
    """
    Runs get_wallet_transactions sequentially (synchronously) for each wallet in search_queries.

    Args:
        search_queries (list[list[str, str, int]]): List of [wallet_address, token_address, top_n]

    Returns:
        dict: { wallet_address: transaction_list }
    """
    results = {}

    for query in search_queries:
        if len(query) != 3:
            continue  # ignore malformed entries

        wallet_address, token_address, top_n = query

        try:
            data = await get_wallet_transactions(wallet_address, token_address or None, int(top_n))
            results[wallet_address] = data
        except Exception as e:
            results[wallet_address] = {"error": str(e)}

    return results
