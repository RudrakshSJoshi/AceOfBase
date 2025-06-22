import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
PER = os.getenv("PERPLEXITY_API_KEY")

async def search_web(query):
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": query}
        ],
        "max_tokens": 300
    }
    headers = {
        "Authorization": f"Bearer {PER}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    # ✅ Parse JSON response
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON response.")
        print("Raw response:", response.text)
        return

    # ✅ Extract citations and response content
    citations = data.get("citations", [])
    choices = data.get("choices", [])
    if choices:
        response_content = choices[0].get("message", {}).get("content", "")
    else:
        response_content = "[No response content]"

    # ✅ Print the results
    # print("📚 Citations:")
    # for url in citations:
    #     print("-", url)

    # print("\n📝 Response Content:\n")
    # print(response_content)

    citation_lines = "\n".join(f"- {url}" for url in citations)
    return (
        "📚 Citations:\n"
        f"{citation_lines}\n\n"
        "📝 Response Content:\n\n"
        f"{response_content}"
    )
