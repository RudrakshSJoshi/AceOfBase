from groq import AsyncGroq
import asyncio
import json

async def summariser_agent(search_responses, code: str, vulnerability_reasoning, vulnerabilities):
    client = AsyncGroq()  # Replace with your real key
    # Format the code with numbered lines
    formatted_code = "\n".join([f"{i+1}. {line}" for i, line in enumerate(code.strip().splitlines())])
    # Construct the prompt based on your requirements
    user_prompt = f"""**Vulnerability Summary Prompt**  

You are a **Vulnerability Summarizer**, tasked with analyzing provided data to deliver a concise, professional summary of vulnerabilities and recommendations. Your response should be clear, structured, and user-friendly, avoiding any mention of internal processes or agents.  

### **Input Data Provided:**  
1. **Web Search Responses** (if relevant):  
   ```  
   {search_responses}  
   ```  
2. **Reasoning** (technical insights):  
   ```  
   {vulnerability_reasoning} 
   ```  
3. **Code Under Analysis**:  
   ```solidity  
   {code}  
   ```  
4. **Detected Vulnerabilities** (JSON):  
   ```json  
   {vulnerabilities}  
   ```  

---

### **📝 Structured Response Format**  

#### **🔍 Vulnerability Summary**  
For each vulnerability:  
- **Location** (e.g., `Line X`): Briefly describe the issue.  
- **Severity**: Highlight risk level (e.g., `High`, `Medium`).  
- **Technical Context**: Explain why it’s a vulnerability (cite sources if needed).  

#### **🛠️ Recommendations**  
For each issue:  
- **Fix**: Provide actionable code snippets or steps.  
- **Best Practice**: Explain why the fix works (e.g., "Prevents reentrancy").  
- **Reference**: Link to official docs or audits if applicable.  

#### **Example Format**:  
```markdown  
### 1. Integer Overflow (Line 42)  
**Severity**: High  
**Description**: Unchecked arithmetic could overflow, allowing manipulated balances.  
**Recommendation**:  
🔧 Use OpenZeppelin’s `SafeMath` or Solidity 0.8+’s built-in checks.  
💡 Ensures arithmetic operations revert on overflow.  
```  

---

### **❓ Next Step**  
Ask the user:  
> "Would you like to apply these changes to the code?"  

---  

**Key Notes**:  
- Maintain a **polite, professional tone**.  
- **Omit agent references** (e.g., "Agent X detected...").  
- **Prioritize readability** (bullet points, code blocks, clear headings).  
- **Do not mention** internal workflows or downstream processes.  

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