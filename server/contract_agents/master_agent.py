from groq import AsyncGroq
import asyncio
import json

async def master_agent(code: str, classification_result: str):
    client = AsyncGroq()  # Replace with your real key
    # Format the code with numbered lines
    formatted_code = "\n".join([f"{i+1}. {line}" for i, line in enumerate(code.strip().splitlines())])
    # Construct the prompt based on your requirements
    user_prompt = f"""
You are provided with a code. It should understand the **context** below, and it should check the **code** for vulnerabilities (all of them). It can take the help of the **classification_result** to check exactly what the classifier has output, and see if the classifier is right or not.

This part is only for thinking (CoT - Chain of Thought), so **think about what kind of vulnerabilities may be present**.

---

### Code:
{formatted_code}
---

### Classification Result:
{classification_result}

---

You are a **BaseModel** agent with the following capability schema:

```python
class BaseModel:
    searches: list[str]         # Web search queries
    vulnerability_reasoning: str  # RAG (retrieval augmented generation) input queries
    vulnerabilities: list[list[int, str, str]]  # List of detected vulnerabilities with line number, content, and type
````

You can perform:

* **Web Searches**: to find relevant information on possible vulnerabilities or known issues in similar code.
* **Vulnerability Reasoning**: to fetch contextual understanding of what a vulnerability means or how it might behave, and pass this info to other agents.
* **Vulnerability Analysis**: to analyze the code for specific vulnerabilities, and regions where they might occur.

**Important Notes**:

* You may give upto 3 searches.
* You are **not** supposed to make any final decisions or give verdicts.
* You are **only** responsible for invoking `searches`, `vulnerability_reasoning`, and `vulnerabilities` to help the next agent in the chain.
* Focus on the **meaning, presence, or possible triggers** of the following vulnerabilities:

1. Integer Overflows
2. Unchecked External Call
3. Reentrancy
4. Dangerous Delegatecall
5. Timestamp Dependency
6. Block Number Dependency
7. Ether Frozen
8. Ether Strict Equality

Respond in **JSON** format:

```json
{{
    "searches": ["..."],
    "vulnerability_reasoning": str,
    "vulnerabilities": [[line number, line content, vulnerability type], ...]
}}
```

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