from groq import AsyncGroq
import asyncio

async def token_analyst_agent(token_report: str):
    client = AsyncGroq()
    
    user_prompt = f"""
You are an advanced blockchain token security analyst. Analyze this token security report (provided as raw text) and provide a comprehensive assessment.

### Raw Token Security Report:
{token_report}

---

### Analysis Instructions:

1. **Parse and Understand**:
   - Extract key-value pairs from the raw text
   - Interpret numeric flags (0 = safe, 1 = risky)
   - Handle None/Null values appropriately

2. **Security Assessment**:
   - Analyze creator/owner relationships
   - Check tax and transfer restrictions
   - Evaluate contract risks

3. **Risk Summary**:
   - Categorize risk level (Safe/Low/Medium/High/Critical)
   - Explain justification for the rating
   - Highlight any honeypot potential

4. **Generate Report**:
   - Follow the exact markdown format below
   - Include all specified sections
   - Make recommendations actionable

---

### Response Format (You will not use Markdown tags, those are just for formatting for your understanding):
```markdown
## Token Security Assessment

### Basic Information
- **Token Name**: [extracted from report]
- **Token Symbol**: [extracted from report]
- **Creator Address**: [extracted from report]
- **Total Supply**: [extracted from report]
- **Holder Count**: [extracted from report]

### Security Indicators Summary
✅ Safe Features: 
  - [Feature 1]
  - [Feature 2]
  
⚠️ Potential Risks: 
  - [Risk 1]
  - [Risk 2]
  
❌ Dangerous Features: 
  - [Danger 1] (if any)

### Risk Level Assessment
**Overall Risk**: [Safe/Low/Medium/High/Critical]  
**Confidence**: [High/Medium/Low]  
**Rationale**: [detailed explanation]

### Detailed Security Analysis
1. **Contract Safety**:
   - Open Source: [Yes/No]
   - Proxy Contract: [Yes/No]
   - Mintable: [Yes/No]

2. **Tokenomics**:
   - Buy Tax: [X]%
   - Sell Tax: [X]%
   - Creator Holdings: [X]%

3. **Risky Functionality**:
   - Hidden Owner: [Yes/No]
   - Transfer Pausable: [Yes/No]
   - Ownership Takeback: [Yes/No]

### Behavioral Analysis
- [Pattern 1]
- [Pattern 2]
- [Anomaly detection]

### Recommendations
- [Actionable recommendation 1]
- [Actionable recommendation 2]
- [Preventive measures]
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