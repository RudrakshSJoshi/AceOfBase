from groq import AsyncGroq
import asyncio
import json

async def code_updater_agent(code, changes):
    client = AsyncGroq()  # Replace with your real key
    
    user_prompt = f"""
You are the **Elite Code Updater Agent**, an expert at precisely modifying code while maintaining perfect style and readability.

**Your Mission:**
1. Carefully analyze the original code: {code}
2. Review the requested changes: {changes}
3. Apply chain-of-thought reasoning to determine the optimal implementation
4. Enhance the code with:
   - Clear, concise comments explaining changes
   - Perfect formatting and style
   - All necessary safety checks
   - Improved readability without altering functionality

**Implementation Rules:**
- Think step-by-step before making changes
- Add explanatory comments for each modification
- Preserve existing comments and style
- Only make changes specifically requested
- Ensure backward compatibility
- Mark changes with '// MODIFIED' comments

**Output Format:**
- Return ONLY the final updated code
- NO markdown tags (``` ```)
- NO additional explanations
- JUST the pure code with your improvements
- If you add markdown tags, you will be severely penalized

**Chain of Thought Process:**
1. Analyze original code structure
2. Verify each requested change
3. Plan implementation strategy
4. Add safety checks if needed
5. Write clear comments
6. Validate changes don't break existing functionality

Now update the code with these changes while following all guidelines perfectly.
"""

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
    return data